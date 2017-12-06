"use strict";

import {Events, UiEvent} from "../events/events.js";

/**
 * Provides a wrapper which binds all supported gestures to a given canvas and scene graph.
 */
export default class GesturesManager {
  constructor(canvas, sceneGraph, messageBus) {
    this._canvas = canvas;
    this._messageBus = messageBus;
    this._sceneGraph = sceneGraph;
    this._dragMode = false;

    this._canvasX = undefined;
    this._canvasY = undefined;

    this._messageBus.on(Events.gestures.CLOSE_EDITOR, (evt) => {
      this._closeEditor(evt.node);
    });
  }

  init() {
    const rect = this._canvas.getBoundingClientRect();
    this._canvasX = rect.x;
    this._canvasY = rect.y;
    this._canvasWidth = rect.width;
    this._canvasHeight = rect.canvasHeight;

    this._handleMouseDown();
    this._handleMouseMove();
    this._handleMouseUp();
    this._handleDoubleClick();
    this._handleKeyDown();
  }

  _closeEditor(editor) {
    this._showElement(false, editor);
  }

  _getCanvasPoint(x, y) {
    /*
     * TODO (cosnita) take in consideration scroll offset and other possible boundaries which might influence
     * the absolute position within the canvas.
     */
    const pr = window.devicePixelRatio;
    x = (x - this._canvasX) * pr;
    y = (y - this._canvasY) * pr;

    return [x, y];
  }

  _getScreenPoint(x, y) {
    const pr = window.devicePixelRatio;
    x = x / pr + this._canvas.offsetLeft;
    y = y / pr + this._canvas.offsetTop;

    return [x, y];
  }

  _handleMouseDown() {
    this._canvas.addEventListener("mousedown", (evt) => {
      this._canvas.tabIndex = 1;

      if (this._sceneGraph.selectedNode && this._sceneGraph.selectedNode.editorUI) {
        this._showElement(false, this._sceneGraph.selectedNode.editorUI.domElement);
        this._sceneGraph.deselect();
      }

      const [x, y] = this._getCanvasPoint(evt.pageX, evt.pageY);
      this._sceneGraph.select(x, y);

      if (this._sceneGraph.selectedNode) {
        this._dragMode = true;
      }

      this._invalidateSceneGraph();
    });
  }

  _handleMouseMove() {
    this._canvas.addEventListener("mousemove", (evt) => {
      if (this._sceneGraph.selectedNode && this._dragMode) {
        const [x, y] = this._getCanvasPoint(evt.pageX, evt.pageY);
        this._sceneGraph.moveSelection(x, y);
        this._invalidateSceneGraph();
      }
    });
  }

  _handleMouseUp() {
    this._canvas.addEventListener("mouseup", (evt) => {
      this._dragMode = false;
      this._invalidateSceneGraph();
    });
  }

  _handleDoubleClick() {
    this._canvas.addEventListener("dblclick", (evt) => {
      evt.preventDefault();
      const [x, y] = this._getCanvasPoint(evt.pageX, evt.pageY);
      const selectedNode = this._sceneGraph.select(x, y);

      if (!selectedNode) {
        return;
      }

      let editorUI = selectedNode.editorUI;
      if (!editorUI) { return; }

      editorUI.restore({
        "model": selectedNode.model,
        "messageBus": this._messageBus,
      });
      this._showElement(true, editorUI.domElement);

      let [editorX, editorY] = this._getScreenPoint(selectedNode.x, selectedNode.y);
      editorX += 10;
      editorY += 10;

      editorUI.domElement.focus();
      editorUI.setPosition(editorX, editorY);
      this._invalidateSceneGraph();
    });
  }

  _handleKeyDown() {
    this._canvas.addEventListener("keydown", (evt) => {
      const selectedNode = this._sceneGraph.selectedNode;
      const evtName = Events.gestures.DELETE_NODE;

      switch (evt.keyCode) {
        case 8:
        case 46:
          this._messageBus.emit(evtName, new UiEvent(evtName, {
            "sceneGraph": this._sceneGraph,
            "node": selectedNode,
          }));
          break;
        default:
          Events.invalidateSceneGraph(this._sceneGraph);
      }
    });
  }

  _invalidateSceneGraph() {
    Events.invalidateSceneGraph(this._sceneGraph);
  }

  _showElement(visible, editor) {
    editor.style.visibility = visible ? "visible" : "hidden";
  }
}
