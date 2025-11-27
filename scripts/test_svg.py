from svgpathtools import parse_path, Path
from xml.etree.ElementTree import Element, SubElement, tostring
from dataclasses import dataclass


@dataclass
class RailPathConfig:
    centerline: str
    num_points: int
    rail_guage: float
    rail_width: float
    tie_length: float
    tie_spacing: float
    tie_thickness: float


class SvgPath:
    def __init__(self, config: RailPathConfig):
        self._path_str: str = config.centerline
        self._path: Path = parse_path(self._path_str)
        self._elements = []

        num_ties: int = round(self._path.length() / config.tie_spacing)
        self.ties(
            num_ties=num_ties, length=config.tie_length, thickness=config.tie_thickness
        )

        self.rails(
            num_points=config.num_points,
            offset=(config.rail_guage + config.rail_width) / 2,
            thickness=config.rail_width,
        )

        self.centerline()

        self.anchors()

        self._bbox: tuple[complex, complex] = self.box(num_points=config.num_points, offset=config.tie_length / 2)

    def point(self, t: float) -> complex:
        return self._path.point(t)

    def tangent(self, t: float) -> complex:
        return self._path.unit_tangent(t)

    def normal(self, t: float) -> complex:
        tan = self.tangent(t)
        return complex(-tan.imag, tan.real)

    def sample(self, num_points: int, offset: float = 0) -> list[complex]:
        points: list[complex] = []
        for i in range(num_points):
            t = i / (num_points - 1)
            pt = self.point(t)
            norm = self.normal(t)
            points.append(pt + norm * offset)
        return points

    def add_element(self, zindex: int, type: str, **attrs) -> None:
        self._elements.append((zindex, type, attrs))

    def centerline(self) -> None:
        self.add_element(
            5, "path", d=self._path_str, stroke="green", fill="none", stroke_width="1"
        )

    def _arrow(self, base: complex, tan: complex, norm: complex, length: float, size: float) -> None:
        p0 = base
        p1 = p0 + tan * (length - size)
        p2 = p1 + norm * size
        p3 = p0 + tan * length
        p4 = p1 - norm * size
        arrow = (
            f"M {p0.real},{p0.imag} "
            f"L {p1.real},{p1.imag} "
            f"L {p2.real},{p2.imag} "
            f"L {p3.real},{p3.imag} "
            f"L {p4.real},{p4.imag} "
            f"L {p1.real},{p1.imag} "
            f"Z"
        )
        self.add_element(6, "path", d=arrow, fill="red", stroke="red")


    def anchors(self) -> None:
        length = 8
        size = 1
        def rotate(v: complex) -> complex:
            return complex(-v.imag, v.real)
        self._arrow(self.point(0), self.tangent(0), self.normal(0), length, size)
        self._arrow(self.point(0), self.normal(0), rotate(self.normal(0)), length, size)
        self._arrow(self.point(1), self.tangent(1), self.normal(1), length, size)
        self._arrow(self.point(1), self.normal(1), rotate(self.normal(1)), length, size)

    def _rail(self, num_points: int, offset: float, thickness: float) -> None:
        outer = self.sample(num_points, offset - thickness / 2)
        inner = self.sample(num_points, offset + thickness / 2)
        points: list[complex] = outer + inner[::-1]
        points_str = " ".join(f"{p.real},{p.imag}" for p in points)
        self.add_element(4, "polygon", points=points_str, fill="grey")

    def rails(self, num_points: int, offset: float, thickness: float) -> None:
        self._rail(num_points, offset, thickness)
        self._rail(num_points, -offset, thickness)

    def _tie(self, t: float, length: float, thickness: float) -> None:
        pt = self.point(t)
        tan = self.tangent(t)
        norm = self.normal(t)

        half_cap = thickness / 2
        half_tie = length / 2 - half_cap

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
        self.add_element(1, "path", d=path_str, fill="sienna")

    def ties(self, num_ties: int, length: float, thickness: float) -> None:
        path_length = self._path.length()
        spacing = path_length / num_ties
        for i in range(num_ties):
            s = (i + 0.5) * spacing
            t = self._path.ilength(s)
            self._tie(t, length, thickness)

    @staticmethod
    def _bounding_box(points: list[complex]) -> tuple[complex, complex]:
        """
        Returns (top_left, bottom_right) as complex numbers from a list of complex points.
        """
        if not points:
            raise ValueError("points list cannot be empty")

        xs = [p.real for p in points]
        ys = [p.imag for p in points]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        top_left = complex(min_x, min_y)
        bottom_right = complex(max_x, max_y)

        return top_left, bottom_right

    def box(self, num_points: int, offset: float) -> tuple[complex, complex]:
        outer = self.sample(num_points, offset)
        inner = self.sample(num_points, -offset)
        points: list[complex] = outer + inner[::-1]
        points_str = " ".join(f"{p.real},{p.imag}" for p in points)
        self.add_element(10, "polygon", points=points_str, fill="pink", opacity="0.2")
        return self._bounding_box(points)

    def data(self) -> bytes:
        svg = Element("svg", xmlns="http://www.w3.org/2000/svg")
        for _, type, attrs in sorted(self._elements, key=lambda e: e[0]):
            SubElement(svg, type, **attrs)
        bb0, bb1 = self._bbox
        buffer = 10
        svg.set(
            "viewBox",
            f"{bb0.real - buffer} {bb0.imag - buffer} {bb1.real - bb0.real + 2 * buffer} {bb1.imag - bb0.imag + 2 * buffer}",
        )
        return tostring(svg)



config = RailPathConfig(
    centerline="M 0,0 L 250,0",
    num_points=200,
    rail_guage=31.75,
    rail_width=3,
    tie_length=45,
    tie_spacing=10,
    tie_thickness=3.5,
)
with open("lionel/tracks/straight.svg", "wb") as f:
    f.write(SvgPath(config).data())


config = RailPathConfig(
    centerline="M 0,0 L 100,0",
    num_points=200,
    rail_guage=31.75,
    rail_width=3,
    tie_length=45,
    tie_spacing=10,
    tie_thickness=3.5,
)
with open("lionel/tracks/short.svg", "wb") as f:
    f.write(SvgPath(config).data())

config = RailPathConfig(
    centerline="M 0,0 A 381,381 0 0,0 231.5,-77.2",
    num_points=200,
    rail_guage=31.75,
    rail_width=3,
    tie_length=45,
    tie_spacing=10,
    tie_thickness=3.5,
)
with open("lionel/tracks/curve381.svg", "wb") as f:
    f.write(SvgPath(config).data())
