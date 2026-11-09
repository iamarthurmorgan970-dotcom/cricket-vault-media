"""Geometry for True Scale: country rings, projections, true-shape moves on the sphere."""
import json
import numpy as np
from shapely.geometry import shape, Polygon, MultiPolygon

import os
DATA = os.environ.get("TS_DATA", os.path.expanduser("~/.cache/true-scale"))


def _rings(geom, tol):
    polys = geom.geoms if isinstance(geom, MultiPolygon) else [geom]
    out = []
    for p in polys:
        q = p.simplify(tol, preserve_topology=True) if tol else p
        if q.is_empty:
            continue
        for qq in (q.geoms if isinstance(q, MultiPolygon) else [q]):
            a = np.asarray(qq.exterior.coords)
            if len(a) >= 4:
                out.append(a.copy())
    return out


def load_world(tol=0.04, min_area=0.02):
    d = json.load(open(f"{DATA}/countries50.geojson"))
    countries, continent = {}, {}
    for f in d["features"]:
        n = f["properties"]["ADMIN"]
        g = shape(f["geometry"])
        polys = g.geoms if isinstance(g, MultiPolygon) else [g]
        keep = [p for p in polys if p.area >= min_area] or list(polys)
        countries[n] = _rings(MultiPolygon(keep) if len(keep) > 1 else keep[0], tol)
        continent[n] = f["properties"]["CONTINENT"]
    return countries, continent


def split_usa(rings):
    alaska, lower48, other = [], [], []
    for r in rings:
        cx, cy = r[:, 0].mean(), r[:, 1].mean()
        if cy > 50 and (cx < -129 or cx > 170):
            alaska.append(r)
        elif -130 < cx < -60 and 23 < cy < 50:
            lower48.append(r)
        else:
            other.append(r)
    return alaska, lower48, other


# ------------------------------------------------------------------ projections (outputs in "degree-like" units)
def mercy(lat):
    lat = np.clip(lat, -85.0, 85.0)
    return np.degrees(np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)))


def merc(a):
    return np.column_stack([a[:, 0], mercy(a[:, 1])])


_A1, _A2, _A3, _A4 = 1.340264, -0.081106, 0.000893, 0.003796
_M = np.sqrt(3) / 2
_EE_SCALE = 180.0 / (2 * np.sqrt(3) * np.pi / (3 * _A1))     # x(180°) == 180


def equal_earth(a):
    lam, phi = np.radians(a[:, 0]), np.radians(np.clip(a[:, 1], -90, 90))
    th = np.arcsin(_M * np.sin(phi))
    th2, th6 = th ** 2, th ** 6
    x = 2 * np.sqrt(3) * lam * np.cos(th) / (3 * (9 * _A4 * th6 * th2 + 7 * _A3 * th6 + 3 * _A2 * th2 + _A1))
    y = _A4 * th6 * th2 * th + _A3 * th6 * th + _A2 * th2 * th + _A1 * th
    return np.column_stack([x, y]) * _EE_SCALE


def ortho(a, lon0, lat0, R=1.0):
    lam, phi = np.radians(a[:, 0]), np.radians(a[:, 1])
    l0, p0 = np.radians(lon0), np.radians(lat0)
    cosc = np.sin(p0) * np.sin(phi) + np.cos(p0) * np.cos(phi) * np.cos(lam - l0)
    x = np.cos(phi) * np.sin(lam - l0)
    y = np.cos(p0) * np.sin(phi) - np.sin(p0) * np.cos(phi) * np.cos(lam - l0)
    hidden = cosc < 0
    if hidden.any():                       # push hidden points onto the horizon
        n = np.hypot(x[hidden], y[hidden]) + 1e-12
        x[hidden] /= n
        y[hidden] /= n
    return np.column_stack([x, y]) * R, (~hidden).mean()


# ------------------------------------------------------------------ true-shape moves
def _xyz(lon, lat):
    lam, phi = np.radians(lon), np.radians(lat)
    return np.stack([np.cos(phi) * np.cos(lam), np.cos(phi) * np.sin(lam), np.sin(phi)], axis=-1)


def _lonlat(v):
    return np.degrees(np.arctan2(v[..., 1], v[..., 0])), np.degrees(np.arcsin(np.clip(v[..., 2], -1, 1)))


def _rot(v, k, th):
    k = k / np.linalg.norm(k)
    return v * np.cos(th) + np.cross(k, v) * np.sin(th) + np.outer(v @ k, k) * (1 - np.cos(th))


def move(rings, frm, to, frac):
    """Slide rings (lon/lat) so the point `frm` lands on `to`, keeping true shape and size.
    First a pure longitude shift, then a rotation along the meridian (keeps north up near the shape)."""
    (lon0, lat0), (lon1, lat1) = frm, to
    dlon, dlat = (lon1 - lon0) * frac, (lat1 - lat0) * frac
    lc = lon0 + dlon
    k = np.array([-np.sin(np.radians(lc)), np.cos(np.radians(lc)), 0.0])   # east axis at the equator
    out = []
    for r in rings:
        v = _xyz(r[:, 0] + dlon, r[:, 1])
        v = _rot(v, k, -np.radians(dlat))
        lon, lat = _lonlat(v)
        lon = np.degrees(np.unwrap(np.radians(lon)))
        lon += 360.0 * np.round((lc - lon.mean()) / 360.0)
        out.append(np.column_stack([lon, lat]))
    return out


def ease(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def ease2(x):
    x = np.clip(x, 0.0, 1.0)
    return 0.5 - 0.5 * np.cos(np.pi * x)
