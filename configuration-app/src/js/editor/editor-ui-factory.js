"use strict";

import Api from "../rendering/shapes/api.js";
import Project from "../rendering/shapes/project.js";
import ApiEditor from "./api-editor.js";
import ProjectEditor from "./project-editor.js";

const UI_MAPPINGS = { };
UI_MAPPINGS[Api] = function(opts) { return new ApiEditor(opts || { }); };
UI_MAPPINGS[Project] = function(opts) { return new ProjectEditor(opts || { }); };

/**
 * Provides the factory which can return a specific ui for editing an element.
 * Not all elements which can be rendered are actually editable. This is the reason
 * why we map only the editable ones in this factory.
 */
export default class EditorUIFactory {
  constructor(parentNode) {
    this._parentNode = parentNode || document.body;
    this._uiMappings = UI_MAPPINGS;
    this._cachedMappings = { };
  }

  getEditor(nodeType, opts) {
    const cachedUI = this._cachedMappings[nodeType];
    if (cachedUI) {
      return cachedUI;
    }

    const ui = this._uiMappings[nodeType];
    if (!ui) {
      return;
    }

    const uiInstance = ui(opts);
    this._cachedMappings[nodeType] = uiInstance;
    this._parentNode.appendChild(uiInstance.domElement);
    uiInstance.parentNode = this._parentNode;

    return uiInstance;
  }
}
