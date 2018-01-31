"use strict";

import Editor from "./editor.js";

export default class ProjectEditor extends Editor {
  constructor(opts) {
    super();
    this._component = undefined;
    this._createProjectComponent();
  }

  get domElement() { return this._component; }

  restore(opts) {
    const model = opts.model;
    this._component.projectModel = { };
    this._component.projectModel = model;
    this._component.messageBus = opts.messageBus;
  }

  _createProjectComponent() {
    this._component = document.createElement("configuration-project-details");
    this._component.style.width = "300px";
    this._component.style.height = "300px";
    this._component.style.visibility = "hidden";
    this._component.style.position = "absolute";
    this._component.projectModel = { };
  }
}
