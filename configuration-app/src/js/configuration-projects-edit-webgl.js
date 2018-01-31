"use strict";

import ConfigurationProjectsBasic from "./configuration-projects-base.js";
import {Events, ModelEvent} from "./events/events.js";

export default class ConfigurationProjectsEditWebGl extends ConfigurationProjectsBasic {
  static get is() { return "configuration-projects-edit-webgl"; }

  static get properties() {
    return {
      projects: Array,
      selectedProject: {
        type: Object,
        notify: true,
        observer: "_displayProject",
      },
      projectApis: Array,
    };
  }

  constructor() {
    super();

    this._loadProjects();
  }

  /**
   * Provides the algorithm for clearing the current scenegraph and recreating it for the new project.
   */
  _clearCanvas() {
    Events.newSceneGraph(this._sceneGraph);
  }

  _displayProject(selectedProject) {
    if (!selectedProject) {
      return;
    }

    const projectId = selectedProject.value;
    this._clearCanvas();
    this._loadExistingProject(projectId);
  }

  _loadProjects() {
    Rx.DOM.ajax({  // eslint-disable-line no-undef
      method: "GET",
      url: this._constants.PROJECTS_URL,
      headers: {
        "Content-Type": "application/json",
      },
      responseType: "json",
    })
      .map((data) => data.response.items)
      .map((projects) => projects.filter((p) => p.owner.id === "3746656e-c319-447f-9fc1-2f85f1cbcd33"))
      .subscribe(
        (projects) => {
          this.setProperties({projects: projects});
        },
        (err) => console.log(err)  // eslint-disable-line no-console
      );
  }

  _loadExistingProject(projectId) {
    this._sceneStorageManager.loadScene(projectId, this._supportedNodes).then((projectModel) => {
      this._projectModel = projectModel;

      const evtProjectGet = Events.models.GET_CURRENT_PROJECT_LOADED;
      this._messageBus.emit(evtProjectGet, new ModelEvent(evtProjectGet, {
        "model": this._projectModel,
      }));
    });
  }
}

window.customElements.define(ConfigurationProjectsEditWebGl.is, ConfigurationProjectsEditWebGl);
