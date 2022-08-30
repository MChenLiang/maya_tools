#!/usr/bin/env python
# -*- coding:UTF-8 -*-

# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+ #
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# from __future__ import unicode_literals
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+ #
import pathlib
import pymel.core as pm
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui


# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+ #
def as_api_object(node_name, typ="MObject"):
    """
    根据输入转换为api类型
    MDagPath = asMObject(nodeName, "MDagPath")
    :param node_name: maya node name
    :param typ: return type
    :return: om.MObject or om.MDagPath
    """
    sel = om.MSelectionList()
    sel.add(node_name)
    if typ == "MObject":
        rt = om.MObject()
        sel.getDependNode(0, rt)
    elif typ == "MDagPath":
        rt = om.MDagPath()
        sel.getDagPath(0, rt)
    else:
        raise KeyError("Input typ must be:\"MObject\" or \"MDagPath\"")
    return rt


def _get_curr_panel(curr_cam_trans):
    model_panel = "modelPanel4"
    for panel in cmds.getPanel(allPanels=1):
        if cmds.getPanel(typeOf=panel) != 'modelPanel':
            continue
        if cmds.modelPanel(panel, q=1, cam=1) == curr_cam_trans:
            model_panel = panel

    return model_panel


# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+ #
def main(img_path, mesh_head):
    # get bounding box
    # create cam
    # save image to
    img_path = pathlib.Path(img_path)
    dag_fn = om.MFnDagNode(
        as_api_object(
            mesh_head, "MDagPath"))
    bbox = dag_fn.boundingBox()  # type:om.MBoundingBox
    b_center = bbox.center()  # type:om.MPoint
    b_max = bbox.max()  # type:om.MPoint

    dis = b_max.distanceTo(b_center)
    cam_trans, cam_shape = pm.camera(name="cam_capture")
    pos_t = b_center.x, b_center.y + dis * 0.15, b_center.z + dis * 1.2

    #
    pm.mel.eval('setNamedPanelLayout "Single Perspective View";')
    pm.mel.eval('setCameraNamesVisibility(0);')
    # 获取 panel
    view = omui.M3dView()
    omui.M3dView.get3dView(0, view)

    cam_dag = om.MDagPath()
    view.getCamera(cam_dag)
    curr_cam_trans = om.MFnDagNode(cam_dag.transform()).name()

    model_panel = _get_curr_panel(curr_cam_trans)

    # 设置相机
    dag_path = as_api_object(str(cam_shape), "MDagPath")
    view.setCamera(dag_path)
    curr_cam_mp = _get_curr_panel(str(cam_trans))
    pm.mel.eval('setWireframeOnShadedOption true %s;' % _get_curr_panel(str(cam_trans)))
    # 关闭刷新
    view.refresh(False, True)

    pm.select(mesh_head, r=1)
    pm.mel.eval('fitAllPanels -selectedNoChildren;enableIsolateSelect {} true;'.format(model_panel))
    pm.select(cl=1)

    # hud
    pm.modelEditor(curr_cam_mp, edit=True, hud=False)

    pm.xform(cam_trans, ws=1, t=pos_t)
    cam_shape.orthographic.set(1)
    cam_shape.orthographicWidth.set(36)
    pm.modelEditor(model_panel, e=1, grid=True)

    tp_img = pm.playblast(format='image',
                          compression='png',
                          filename=str(img_path.parent.joinpath(img_path.stem)),
                          widthHeight=(1024, 1024),
                          clearCache=1, viewer=0, showOrnaments=1, percent=100,
                          offScreen=1, quality=100,
                          frame=1, fp=4
                          )
    pm.isolateSelect(model_panel, state=0)
    img_path.exists() and img_path.unlink()
    pathlib.Path(tp_img.replace("####", "0000")).rename(img_path)

    pm.modelEditor(curr_cam_mp, edit=True, hud=True)
    view.setCamera(cam_dag)
    view.refresh(True, True)
    pm.delete(cam_trans)


if __name__ == "__main__":
    pass
