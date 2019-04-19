import argparse
import warnings

import numpy as np
import trimesh
import trimesh.viewer

import skrobot


def show_with_rotation(scene, step=None, init_angles=None, **kwargs):
    if step is None:
        step = (0, np.deg2rad(1), 0)
    if init_angles is None:
        init_angles = (0, 0, 0)

    step = np.asarray(step, dtype=float)
    init_angles = np.asarray(init_angles, dtype=float)

    def callback(scene):
        if hasattr(scene, 'angles'):
            scene.angles += step
        else:
            scene.angles = init_angles
        scene.set_camera(angles=scene.angles)

    return trimesh.viewer.SceneViewer(scene=scene, callback=callback, **kwargs)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--robot',
        choices=['kuka', 'fetch', 'pr2'],
        default='kuka',
        help='robot',
    )
    args = parser.parse_args()

    if args.robot == 'kuka':
        robot = skrobot.robot_models.Kuka()
    elif args.robot == 'fetch':
        robot = skrobot.robot_models.Fetch()
    elif args.robot == 'pr2':
        robot = skrobot.robot_models.PR2()
    else:
        raise ValueError('unsupported robot')

    print('link_list:')
    for link in robot.link_list:
        print('  {}'.format(link))
    print('joint_list:')
    for joint in robot.joint_list:
        print('  {}'.format(joint))

    scene = trimesh.Scene()
    geom = trimesh.creation.box((2, 2, 0.01))
    geom.visual.face_colors = (0.75, 0.75, 0.75)
    scene.add_geometry(geom)

    urdf_model = robot.urdf_robot_model
    assert len(robot.link_list) == len(urdf_model.links)
    for link, urdf_link in zip(robot.link_list, urdf_model.links):
        for visual in urdf_link.visuals:
            transform = np.dot(link.worldcoords().T(), visual.origin)

            if 0:  # show axis
                axis = trimesh.creation.axis(0.01)
                axis.apply_transform(transform)
                scene.add_geometry(axis)

            for mesh in visual.geometry.meshes:
                mesh = mesh.copy()

                # TextureVisuals is usually slow to render
                if not isinstance(mesh.visual, trimesh.visual.ColorVisuals):
                    mesh.visual = mesh.visual.to_color()
                    if mesh.visual.vertex_colors.ndim == 1:
                        mesh.visual.vertex_colors = \
                            mesh.visual.vertex_colors[None].repeat(
                                mesh.vertices.shape[0], axis=0
                            )

                    # default texture color
                    DEFAULT_TEXTURE_COLOR = (255, 255, 255, 255)
                    if (mesh.visual.vertex_colors ==
                            DEFAULT_TEXTURE_COLOR).all():
                        mesh.visual.vertex_colors = \
                            trimesh.visual.DEFAULT_COLOR

                # If color or texture is not specified in mesh file,
                # use information specified in URDF.
                if (
                    (mesh.visual.face_colors ==
                        trimesh.visual.DEFAULT_COLOR).all() and
                    visual.material
                ):
                    if visual.material.texture is not None:
                        warnings.warn(
                            'texture specified in URDF is not supported'
                        )
                    elif visual.material.color is not None:
                        mesh.visual.face_colors = visual.material.color

                mesh.apply_transform(transform)
                scene.add_geometry(mesh)

    show_with_rotation(
        scene,
        init_angles=(np.deg2rad(45), np.deg2rad(0), 0),
        step=(0, 0, np.deg2rad(1)),
        resolution=(800, 800),
    )


if __name__ == '__main__':
    main()