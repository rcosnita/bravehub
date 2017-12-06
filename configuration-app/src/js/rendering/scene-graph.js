"use strict";

import Events from "../events/events.js";
import TextGenerator from "./text-generator.js";

export class Node {
  constructor(opts) {
    opts = opts || {};
    this._verticesValue = opts.vertices;
    this._solidColor = opts.color;
    this._color = undefined;
    this._modelMatrix = glm.mat4();
    this._children = [];
    this._parent = undefined;
    this._textGenerator = TextGenerator;
    this._texture = undefined;
    this._editorUI = undefined;
    this._messageBus = undefined;
    this._sceneGraph = undefined;
  }

  _appendChild(node) {
    this._children.push(node);
    node.parent = this;
    node.sceneGraph = () => this.sceneGraph;
  }

  containsPoint(x, y) { throw new Error("Not implemented ... Every node must provide an implementation ..."); }

  get messageBus() { return this._messageBus; }
  set messageBus(value) { this._messageBus = value; }

  get modelMatrix() { return this._modelMatrix; }
  set modelMatrix(value) { this._modelMatrix = value; }

  get parent() { return this._parent; }
  set parent(p) { this._parent = p; }

  get texture() { return this._texture; }

  set _vertices(vertices) {
    this._verticesValue = vertices;
    this._color = this._correlateColorWithVertices(this._solidColor);
  }

  get _vertices() { return this._verticesValue; }

  get vertices() { return this._verticesValue; }

  get x() { throw new Error("Not implemented ... Every node must provide an implementation ..."); }

  get y() { throw new Error("Not implemented ... Every node must provide an implementation ..."); }

  get color() { return this._color; }

  get textGenerator() { return this._textGenerator; }

  get children() { return this._children; }

  set model(val) { throw new Error("Not implemented ... Every node must provide an implementation ..."); }

  get model() { return this._model; }

  set editorUI(elem) { this._editorUI = elem; }

  get editorUI() {
    if (this._editorUI) {
      this._editorUI.activeNode = this;
    }

    return this._editorUI;
  }

  get sceneGraph() {
    return typeof this._sceneGraph === "function" ? this._sceneGraph() : this._sceneGraph;
  }
  set sceneGraph(value) { this._sceneGraph = value; }

  adjustForDrag(x, y) { throw new Error("Not implemented ... Every node must provide an implementation ..."); }

  render(gl, buffers, model, textureSpec) {
    this._renderTexture(gl, textureSpec);
    this._renderModel(gl, buffers, model);
  }

  setPosition(x, y) {
    this._children.forEach((node) => {
      const offsetX = x - this.x;
      const offsetY = y - this.y;

      node.setPosition(node.x + offsetX, node.y + offsetY);
    });
  }

  _renderModel(gl, buffers, model) { }

  _renderTexture(gl, textureSpec) { }

  /**
   * Provides an algorithm which extrapolate the given RGB color to all available vertices.
   *
   * @param {Array} color a RGB color array.
   * @return {Array} the array describing the colors for all vertices.
   */
  _correlateColorWithVertices(color) {
    const points = this.vertices.length / 2;

    let newColor = [];
    for (let idx = 0; idx < points; idx++) {
      newColor = newColor.concat([
        this._fromRGBValue(color[0]),  // red
        this._fromRGBValue(color[1]),  // green
        this._fromRGBValue(color[2]),  // blue
        1.0]);  // alpha
    }

    return newColor;
  }

  _fromRGBValue(value) {
    return 1.0 * value / 255.0;
  }
}

export default class SceneGraph {
  constructor(messageBus) {
    this._isDirty = true;
    this._messageBus = messageBus;
    this._nodes = [];
    this._selectedNode = undefined;

    this._wireEvents();
  }

  addNode(node) {
    node._sceneGraph = this;
    node._messageBus = this._messageBus;
    this._nodes.splice(0, 0, node);
  }

  removeNode(node) {
    const nodePos = this._nodes.indexOf(node);
    if (nodePos < 0) {
      return;
    }

    this._nodes.splice(nodePos, 1);
  }

  get dirty() { return this._isDirty; }
  set dirty(val) { this._isDirty = val; }

  get nodes() { return this._nodes; }

  get messageBus() { return this._messageBus; }

  get selectedNode() { return this._selectedNode; }

  deselect() {
    if (!this._selectedNode) { return; }

    this._selectedNode = undefined;
  }

  moveSelection(x, y) {
    if (!this._selectedNode) { return; }

    this._selectedNode.adjustForDrag(x, y);
  }

  select(x, y) {
    for (let idx = 0; idx < this._nodes.length; idx++) {
      const node = this._nodes[idx];

      if (node.containsPoint(x, y)) {
        this._selectedNode = node;
        this._selectedNode.adjustForDrag(x, y);
        return this._selectedNode;
      }
    }
  }

  _wireEvents() {
    this._messageBus.on(Events.sceneGraph.INVALIDATE_SCENE, () => {
      this.dirty = true;
    });
  }
}
