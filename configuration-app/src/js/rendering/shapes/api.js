"use strict";

import ShapeModel from "../../models/shape-model.js";
import Rectangle from "./rectangle.js";
import SingleLineText from "./singleline-text.js";

export default class Api extends Rectangle {
  constructor(x, y, width, height, color, apiData) {
    super(x, y, width, height, color);

    this._label = new SingleLineText(0, 0, width, height, color, {
      "size": 1.5,
    });
    this._appendChild(this._label);

    this._modelProxy = ShapeModel.getModel(apiData, () => this.sceneGraph,
      (target, name) => {
        return target[name];
      }, (target, name, value) => {
        target[name] = value;
        this._setText();

        return true;
      });

    this._setText();
  }

  get model() { return this._modelProxy; }

  _getLabel() {
    let label = this.model.path;
    if (this.model.exposedPorts && this.model.exposedPorts.length > 0) {
      label = `:${this.model.exposedPorts[0]} ${label}`;
    }

    return label;
  }

  _setText() {
    this._label.text = this._getLabel();
    this._width = Math.max(this._width, this._label.width);
    this._height = Math.max(this._height, this._label.height);
  }

  render(gl, buffers, model, textureSpec) {
    super.render(gl, buffers, model, textureSpec);
  }
}
