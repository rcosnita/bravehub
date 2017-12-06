"use strict";

import ShapeModel from "../../models/shape-model.js";
import Rectangle from "./rectangle.js";
import SingleLineText from "./singleline-text.js";

export default class Project extends Rectangle {
  constructor(x, y, width, height, color, projectData) {
    super(x, y, width, height, color);

    this._label = new SingleLineText(0, 0, width, 100, color, {
      "size": 1.5,
    });
    this._appendChild(this._label);

    this._domainLabel= new SingleLineText(0, 100, width, 100, color, {
      "size": 1,
    });
    this._appendChild(this._domainLabel);

    this._modelProxy = ShapeModel.getModel(projectData, () => this.sceneGraph,
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

  _setText() {
    this._label.text = `${this.model.name}`;
    this._domainLabel.text = `${this.model.domain}`;
    this._width = Math.max(this._width, this._label.width);
    this._height = Math.max(this._height, this._label.height);
  }

  render(gl, buffers, model, textureSpec) {
    super.render(gl, buffers, model, textureSpec);
  }
}
