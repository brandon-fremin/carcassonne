import svg_path_transform as svgtransform
import svgpathtools as svgtools

house_path = "M19.469 12.594l3.625 3.313c0.438 0.406 0.313 0.719-0.281 0.719h-2.719v8.656c0 0.594-0.5 1.125-1.094 1.125h-4.719v-6.063c0-0.594-0.531-1.125-1.125-1.125h-2.969c-0.594 0-1.125 0.531-1.125 1.125v6.063h-4.719c-0.594 0-1.125-0.531-1.125-1.125v-8.656h-2.688c-0.594 0-0.719-0.313-0.281-0.719l10.594-9.625c0.438-0.406 1.188-0.406 1.656 0l2.406 2.156v-1.719c0-0.594 0.531-1.125 1.125-1.125h2.344c0.594 0 1.094 0.531 1.094 1.125v5.875z"

def tranform(path, cx, cy, sx, sy):
    bounding_box = svgtools.parse_path(path).bbox()
    xmin, xmax, ymin, ymax = bounding_box 
    xdelta = xmax - xmin
    ydelta = ymax - ymin
    path = svgtransform.parse_path(path)
    path = svgtransform.translate_and_scale(path, t=(-xmin, -ymin))
    path = svgtransform.translate_and_scale(path, s=(sx / xdelta, sy / ydelta))
    path = svgtransform.translate_and_scale(path, t=(cx - sx / 2, cy - sy / 2))
    new_path = svgtransform.path_to_string(path)
    new_bounding_box = svgtools.parse_path(new_path).bbox()
    print(f"Old Box: {bounding_box}\nNew Box: {new_bounding_box}")
    return new_path

path = tranform(house_path, 50, 50, 30, 30) 
print(path)