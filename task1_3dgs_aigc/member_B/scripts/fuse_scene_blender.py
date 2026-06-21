#!/usr/bin/env python3
"""Create a fused scene for member B and render multi-view images/video.

This script supports two asset classes used in the final homework package:
- Gaussian/3DGS PLY files with x/y/z and SH color fields. These are sampled and
  visualized as small colored blob meshes for Blender rendering.
- Mesh files such as OBJ/GLB/PLY/FBX.

Run with:
  blender --background --python homework/member_B/scripts/fuse_scene_blender.py -- \
    --manifest homework/member_B/asset_manifest_clear.csv \
    --output-dir homework/member_B/renders/fusion_scene \
    --resolution 1280 720 \
    --views 36
"""

from __future__ import annotations

import argparse
import csv
import math
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SUPPORTED_IMPORTS = {".glb", ".gltf", ".obj", ".ply", ".fbx"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fuse 3D assets and render views.")
    parser.add_argument("--manifest", required=True, help="CSV asset manifest path.")
    parser.add_argument("--output-dir", required=True, help="Directory for rendered PNGs.")
    parser.add_argument("--resolution", nargs=2, type=int, default=(1280, 720))
    parser.add_argument("--views", type=int, default=36)
    parser.add_argument("--camera-radius", type=float, default=2.35)
    parser.add_argument("--camera-height", type=float, default=0.95)
    parser.add_argument("--target-height", type=float, default=0.12)
    parser.add_argument("--max-gaussian-points", type=int, default=8000)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def read_gaussian_ply(path: Path, max_points: int) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float, float]]]:
    with path.open("rb") as f:
        header_lines = []
        while True:
            line = f.readline()
            if not line:
                raise ValueError(f"Invalid PLY header: {path}")
            text = line.decode("ascii", errors="replace").strip()
            header_lines.append(text)
            if text == "end_header":
                break
        if "format binary_little_endian 1.0" not in header_lines:
            raise ValueError(f"Only binary_little_endian PLY is supported: {path}")
        vertex_count = 0
        props = []
        in_vertex = False
        for line in header_lines:
            parts = line.split()
            if len(parts) >= 3 and parts[0] == "element" and parts[1] == "vertex":
                vertex_count = int(parts[2])
                in_vertex = True
                continue
            if parts[:2] == ["element", "face"]:
                in_vertex = False
            if in_vertex and len(parts) == 3 and parts[0] == "property":
                props.append(parts[2])
        prop_index = {name: i for i, name in enumerate(props)}
        required = ["x", "y", "z", "f_dc_0", "f_dc_1", "f_dc_2"]
        missing = [name for name in required if name not in prop_index]
        if missing:
            raise ValueError(f"Missing PLY properties {missing}: {path}")
        stride = 4 * len(props)
        step = max(1, vertex_count // max(1, max_points))
        positions = []
        colors = []
        for idx in range(vertex_count):
            chunk = f.read(stride)
            if not chunk:
                break
            if idx % step != 0:
                continue
            vals = struct.unpack("<" + "f" * len(props), chunk)
            x, y, z = vals[prop_index["x"]], vals[prop_index["y"]], vals[prop_index["z"]]
            # Convert the SH DC term to approximate display RGB.
            r = 0.5 + 0.2820947918 * vals[prop_index["f_dc_0"]]
            g = 0.5 + 0.2820947918 * vals[prop_index["f_dc_1"]]
            b = 0.5 + 0.2820947918 * vals[prop_index["f_dc_2"]]
            colors.append((max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b)), 1.0))
            positions.append((x, y, z))
    return positions, colors


def make_colored_blob_mesh(
    name: str,
    positions: list[tuple[float, float, float]],
    colors: list[tuple[float, float, float, float]],
) -> bpy.types.Object:
    if not positions:
        raise ValueError(f"No positions found for {name}")

    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    zs = [p[2] for p in positions]
    extent = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 1e-6)
    radius = extent * 0.006
    octa_vertices = [
        (radius, 0.0, 0.0),
        (-radius, 0.0, 0.0),
        (0.0, radius, 0.0),
        (0.0, -radius, 0.0),
        (0.0, 0.0, radius),
        (0.0, 0.0, -radius),
    ]
    octa_faces = [
        (4, 0, 2),
        (4, 2, 1),
        (4, 1, 3),
        (4, 3, 0),
        (5, 2, 0),
        (5, 1, 2),
        (5, 3, 1),
        (5, 0, 3),
    ]

    verts = []
    faces = []
    face_point_indices = []
    for point_idx, (x, y, z) in enumerate(positions):
        offset = len(verts)
        verts.extend((x + dx, y + dy, z + dz) for dx, dy, dz in octa_vertices)
        for face in octa_faces:
            faces.append(tuple(offset + i for i in face))
            face_point_indices.append(point_idx)

    mesh = bpy.data.meshes.new(f"{name}_gaussian_blob_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    color_attr = mesh.color_attributes.new(name="display_color", type="BYTE_COLOR", domain="CORNER")
    for polygon, point_idx in zip(mesh.polygons, face_point_indices):
        color = colors[point_idx]
        for loop_idx in polygon.loop_indices:
            color_attr.data[loop_idx].color = color

    obj = bpy.data.objects.new(f"{name}_gaussian_blobs", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def create_gaussian_point_cloud(name: str, path: Path, max_points: int) -> list[bpy.types.Object]:
    positions, colors = read_gaussian_ply(path, max_points)
    obj = make_colored_blob_mesh(name, positions, colors)

    mat = bpy.data.materials.new(f"{name}_point_material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    attr = nodes.new(type="ShaderNodeAttribute")
    attr.attribute_name = "display_color"
    mat.node_tree.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.85
    if name.lower() == "background":
        bsdf.inputs["Base Color"].default_value = (0.18, 0.18, 0.18, 1.0)
        bsdf.inputs["Alpha"].default_value = 0.65
        mat.diffuse_color = (0.18, 0.18, 0.18, 0.65)
    obj.data.materials.append(mat)

    return [obj]


def make_principled_material(name: str, color: tuple[float, float, float, float], roughness: float = 0.55) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def assign_asset_material(asset_name: str, objects: list[bpy.types.Object]) -> None:
    key = asset_name.strip().lower()
    material = None
    if key == "object_b":
        material = make_principled_material("object_B_blue_white_visible", (0.86, 0.92, 1.0, 1.0), 0.42)
    elif key == "object_c":
        material = make_principled_material("object_C_warm_wood_visible", (0.76, 0.43, 0.16, 1.0), 0.58)
    if material is None:
        return
    for obj in objects:
        if obj.type == "MESH":
            obj.data.materials.clear()
            obj.data.materials.append(material)


def import_mesh_asset(path: Path) -> list[bpy.types.Object]:
    suffix = path.suffix.lower()
    before = set(bpy.context.scene.objects)
    if suffix in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif suffix == ".obj":
        bpy.ops.wm.obj_import(filepath=str(path))
    elif suffix == ".ply":
        bpy.ops.import_mesh.ply(filepath=str(path))
    elif suffix == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(path))
    else:
        raise ValueError(f"Unsupported asset format: {path}")
    after = set(bpy.context.scene.objects)
    objects = list(after - before)
    for obj in objects:
        if obj.type == "MESH" and not obj.data.materials:
            mat = bpy.data.materials.new(f"{obj.name}_mat")
            mat.diffuse_color = (0.8, 0.8, 0.8, 1.0)
            obj.data.materials.append(mat)
    return objects


def normalize_objects(objects: list[bpy.types.Object], target_extent: float) -> None:
    mesh_objects = [obj for obj in objects if obj.type == "MESH"]
    if not mesh_objects:
        return

    # Bake importer transforms so each asset is normalized in a shared local space.
    for obj in mesh_objects:
        obj.data.transform(obj.matrix_world)
        obj.matrix_world.identity()

    coords = [v.co.copy() for obj in mesh_objects for v in obj.data.vertices]
    if not coords:
        return
    min_v = Vector((min(v.x for v in coords), min(v.y for v in coords), min(v.z for v in coords)))
    max_v = Vector((max(v.x for v in coords), max(v.y for v in coords), max(v.z for v in coords)))
    center = (min_v + max_v) * 0.5
    extent = max(max_v.x - min_v.x, max_v.y - min_v.y, max_v.z - min_v.z, 1e-6)
    scale = target_extent / extent

    for obj in mesh_objects:
        for vertex in obj.data.vertices:
            vertex.co = (vertex.co - center) * scale
        obj.data.update()


def target_extent_for(row: dict[str, str]) -> float:
    name = row["name"].strip().lower()
    kind = row["type"].strip().lower()
    if name == "background":
        return 2.6
    if kind == "gaussian_ply":
        return 0.85
    return 0.9


def group_objects(name: str, objects: list[bpy.types.Object]) -> bpy.types.Object:
    empty = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(empty)
    for obj in objects:
        obj.parent = empty
    return empty


def apply_transform(empty: bpy.types.Object, row: dict[str, str]) -> None:
    empty.location = tuple(float(row[k]) for k in ["location_x", "location_y", "location_z"])
    empty.rotation_euler = tuple(math.radians(float(row[k])) for k in ["rotation_x_deg", "rotation_y_deg", "rotation_z_deg"])
    scale = float(row["scale"])
    empty.scale = (scale, scale, scale)


def load_manifest(manifest: Path) -> list[dict[str, str]]:
    with manifest.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def setup_lighting() -> None:
    bpy.ops.object.light_add(type="AREA", location=(0.0, -3.0, 4.0))
    key = bpy.context.object
    key.name = "Key_Area_Light"
    key.data.energy = 850
    key.data.size = 5.5
    bpy.ops.object.light_add(type="POINT", location=(-2.5, 2.0, 2.0))
    fill = bpy.context.object
    fill.name = "Fill_Light"
    fill.data.energy = 120


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_camera(radius: float, height: float, target_height: float) -> bpy.types.Object:
    bpy.ops.object.camera_add(location=(0, -radius, height))
    camera = bpy.context.object
    camera.name = "Render_Camera"
    camera.data.lens = 30
    camera.data.dof.use_dof = False
    bpy.context.scene.camera = camera
    look_at(camera, Vector((0, 0, target_height)))
    return camera


def configure_render(width: int, height: int) -> None:
    scene = bpy.context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    # Cycles CPU avoids the EGL/OpenGL context issues common on headless servers.
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.cycles.preview_samples = 8
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.world = scene.world or bpy.data.worlds.new("World")
    scene.world.color = (0.04, 0.045, 0.05)


def render_views(camera: bpy.types.Object, output_dir: Path, views: int, radius: float, height: float, target_height: float) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = Vector((0.0, 0.0, target_height))
    for idx in range(views):
        angle = 2.0 * math.pi * idx / views
        camera.location = (radius * math.sin(angle), -radius * math.cos(angle), height)
        look_at(camera, target)
        bpy.context.scene.render.filepath = str(output_dir / f"view_{idx:03d}.png")
        bpy.ops.render.render(write_still=True)


def save_scene(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_dir / "fusion_scene.blend"))


def main() -> None:
    args = parse_args()
    manifest = Path(args.manifest).resolve()
    root = manifest.parent
    output_dir = Path(args.output_dir).resolve()
    clear_scene()

    for row in load_manifest(manifest):
        asset_path = (root / row["path"]).resolve()
        kind = row["type"].strip().lower()
        if not asset_path.exists():
            raise FileNotFoundError(asset_path)
        if kind == "gaussian_ply":
            objects = create_gaussian_point_cloud(row["name"], asset_path, args.max_gaussian_points)
        elif asset_path.suffix.lower() in SUPPORTED_IMPORTS:
            objects = import_mesh_asset(asset_path)
        else:
            raise ValueError(f"Unsupported asset for {row['name']}: {asset_path}")
        normalize_objects(objects, target_extent_for(row))
        assign_asset_material(row["name"], objects)
        empty = group_objects(row["name"], objects)
        apply_transform(empty, row)

    setup_lighting()
    camera = setup_camera(args.camera_radius, args.camera_height, args.target_height)
    configure_render(args.resolution[0], args.resolution[1])
    save_scene(output_dir)
    render_views(camera, output_dir, args.views, args.camera_radius, args.camera_height, args.target_height)


if __name__ == "__main__":
    main()
