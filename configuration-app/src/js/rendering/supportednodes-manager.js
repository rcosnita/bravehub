"use strict";

import Api from "./shapes/api.js";
import Project from "./shapes/project.js";

import ApiModel from "../models/api-model.js";
import ProjectModel from "../models/project-model.js";

class SupportedNodesManager {
  /**
   * Obtains the supported nodes factory instance.
   *
   * @param {EditorFactory} editorFactory
   * @param {EventEmitter} messageBus
   * @return {void}
   */
  getSupported(editorFactory, messageBus) {
    return {
      "project": {
        "shape": Project,
        "background": [0, 128, 255],
        "getShape": function() {
          const shape = new this.shape(0, 0, 500, 300, this.background, new ProjectModel({  // eslint-disable-line new-cap
            "name": "project 1",
            "domain": "www.myproject.com",
          }));
          shape.type = "project";

          shape.editorUI = editorFactory.getEditor(this.shape);
          shape.editorUI.restore({
            "messageBus": messageBus,
            "model": shape.model,
          });

          return shape;
        },
      },
      "api": {
        "shape": Api,
        "background": [255, 0, 0],
        "getShape": function() {
          const shape = new this.shape(0, 0, 500, 300, this.background,  // eslint-disable-line new-cap
                                       new ApiModel({"path": "<your api>"}));
          shape.type = "api";

          shape.editorUI = editorFactory.getEditor(this.shape);
          shape.editorUI.restore({
            "messageBus": messageBus,
            "model": shape.model,
          });

          return shape;
        },
      },
    };
  }
}

export default new SupportedNodesManager();
