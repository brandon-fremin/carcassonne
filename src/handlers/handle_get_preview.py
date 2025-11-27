import svgpathtools

from src.common.utils import http_timer
from dataclasses import dataclass


@dataclass
class RailGuage:
    rail_width: float
    rail_thickness: float
    tie_length: float
    tie_thickness: float
    tie_spacing: float


def ties(centerline: str, guage: RailGuage) -> list[str]:
    path = svgpathtools.parse_path(centerline)
    path_length = path.length()
    num_ties = round(path_length / guage.tie_spacing)
    spacing = path_length / num_ties
    ties_list = []
    for i in range(num_ties):
        s = (i + 0.5) * spacing
        t = path.ilength(s)
        pt: complex = path.point(t)
        tan: complex = path.unit_tangent(t)
        norm = complex(-tan.imag, tan.real)

        half_cap = guage.tie_thickness / 2
        half_tie = guage.tie_length / 2 - half_cap

        p1 = pt + norm * half_tie - tan * half_cap
        p2 = pt + norm * half_tie + tan * half_cap
        p3 = pt - norm * half_tie + tan * half_cap
        p4 = pt - norm * half_tie - tan * half_cap

        path_str = (
            f"M {p1.real},{p1.imag} "
            f"A {half_cap},{half_cap} 0 0,0 {p2.real},{p2.imag} "
            f"L {p3.real},{p3.imag} "
            f"A {half_cap},{half_cap} 0 0,0 {p4.real},{p4.imag} Z"
        )
        ties_list.append({
            "path": path_str,
        })
    return ties_list

def rails(centerline: str, guage: RailGuage, num_points: int) -> list[str]:
    path = svgpathtools.parse_path(centerline)

    def rail_path(offset: float) -> str:
        outer = []
        inner = []
        for i in range(num_points):
            t = i / (num_points - 1)
            pt: complex = path.point(t)
            tan: complex = path.unit_tangent(t)
            norm = complex(-tan.imag, tan.real)
            outer_pt = pt + norm * (offset - guage.rail_thickness / 2)
            inner_pt = pt + norm * (offset + guage.rail_thickness / 2)
            outer.append(outer_pt)
            inner.append(inner_pt)
        points: list[complex] = outer + inner[::-1]
        points_str = " ".join(f"{p.real},{p.imag}" for p in points)
        return points_str

    return [
        {
            "path": rail_path(-guage.rail_width / 2 - guage.rail_thickness / 2)
        }, 
        {
            "path": rail_path(guage.rail_width / 2 + guage.rail_thickness / 2)
        }
    ]

def anchors(centerline: str) -> list[str]:
    path = svgpathtools.parse_path(centerline)
    anchors_list = []

    def arrow_path(base: complex, tan: complex, norm: complex, length: float, size: float) -> str:
        p0 = base
        p1 = p0 + tan * (length - size)
        p2 = p1 + norm * size
        p3 = p0 + tan * length
        p4 = p1 - norm * size
        arrow_path = (
            f"M {p0.real},{p0.imag} "
            f"L {p1.real},{p1.imag} "
            f"L {p2.real},{p2.imag} "
            f"L {p3.real},{p3.imag} "
            f"L {p4.real},{p4.imag} "
            f"L {p1.real},{p1.imag} "
            f"Z"
        )
        return arrow_path

    length = 8
    size = 1

    # Start anchor
    t0 = 0.0
    pt0: complex = path.point(t0)
    tan0: complex = path.unit_tangent(t0)
    norm0 = complex(-tan0.imag, tan0.real)
    anchors_list.append({
        "id": "start",
        "type": "female",
        "tangent": arrow_path(pt0, tan0, norm0, length, size),
        "normal": arrow_path(pt0, norm0, complex(-norm0.imag, norm0.real), length, size)
    })

    # End anchor
    t1 = 1.0
    pt1: complex = path.point(t1)
    tan1: complex = path.unit_tangent(t1)
    norm1 = complex(-tan1.imag, tan1.real)
    anchors_list.append({
        "id": "end",
        "type": "male",
        "tangent": arrow_path(pt1, tan1, norm1, length, size),
        "normal": arrow_path(pt1, norm1, complex(-norm1.imag, norm1.real), length, size)
    })

    return anchors_list


def bounding_box(paths: list[str]) -> dict:
    all_x = []
    all_y = []
    for pstr in paths:
        # Handle both SVG path strings and polygon point strings
        if pstr.strip().startswith(('M', 'L', 'C', 'Q', 'A', 'Z', 'H', 'V', 'S', 'T', 'm', 'l', 'c', 'q', 'a', 'z', 'h', 'v', 's', 't')):
            # It's an SVG path
            p = svgpathtools.parse_path(pstr)
            xmin, xmax, ymin, ymax = p.bbox()
            all_x.extend([xmin, xmax])
            all_y.extend([ymin, ymax])
        else:
            # It's a polygon points string (x,y x,y x,y...)
            points = pstr.strip().split()
            for point in points:
                x, y = map(float, point.split(','))
                all_x.append(x)
                all_y.append(y)
    return {
        "xmin": min(all_x),
        "xmax": max(all_x),
        "ymin": min(all_y),
        "ymax": max(all_y),
    }


def make_centerline(centerline: str, anchors: list[dict]) -> list[dict]:
    return {
        "path": centerline,
        "startAnchorId": anchors[0]["id"],
        "endAnchorId": anchors[1]["id"],
    }


GAUGES = {
    "standard": RailGuage(
        rail_width=20,
        rail_thickness=2,
        tie_length=28,
        tie_thickness=2,
        tie_spacing=10.0
    )
}


@http_timer
def handle_get_preview(req: dict) -> dict:
    centerline: str = req.get("path")
    assert centerline is not None, "Path parameter is required"
    centerline = centerline.strip()

    gauge: str | dict = req.get("gauge", "standard")
    gauge_config = (
        GAUGES.get(gauge)
        if isinstance(gauge, str)
        else RailGuage(**gauge)
    )
    result = {
        "ties": ties(centerline, gauge_config),
        "rails": rails(centerline, gauge_config, 100),
        "anchors": anchors(centerline)
    }
    result["boundingBox"] = bounding_box([
        *[tie["path"] for tie in result["ties"]],
        *[rail["path"] for rail in result["rails"]],
        *[anchor["tangent"] for anchor in result["anchors"]],
        *[anchor["normal"] for anchor in result["anchors"]]
    ])
    result["centerlines"] = [
        make_centerline(centerline, result["anchors"])
    ]
    return result