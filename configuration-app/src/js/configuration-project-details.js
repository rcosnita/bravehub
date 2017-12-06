"use strict";

import {Events, ModelEvent, UiEvent} from "./events/events.js";

class ConfigurationProjectDetails extends Polymer.Element {
  static get is() { return "configuration-project-details"; }

  static get properties() {
    return {
      projectModel: {
        type: Object,
        notify: true,
        observer: "_whenProjectModel",
      },
      messageBus: {
        type: Object,
        notify: true,
        observer: "_whenMessageBus",
      },
    };
  }

  constructor() {
    super();
    this._constants = window.Bravehub.Constants;
  }

  createProject() {
    const action = Rx.DOM.ajax({  // eslint-disable-line no-undef
      url: this._constants.PROJECTS_URL,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(this.projectModel),
    });

    action.subscribe(
      (resp) => this._handleProjectCreated(resp),
      (err) => console.log(err)  // eslint-disable-line no-console
    );
  }

  _handleProjectCreated(resp) {
    alert("Project created successfully ...");
    const projectLocation = resp.xhr.getResponseHeader("Location");

    const loader = Rx.DOM.ajax({  // eslint-disable-line no-undef
      url: projectLocation,
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    loader.subscribe(
      (resp) => this._handleProjectLoaded(projectLocation, resp),
      (err) => console.log(err)  // eslint-disable-line no-console
    );
  }

  _handleProjectLoaded(projectLocation, resp) {
    Object.assign(this.projectModel, JSON.parse(resp.response));
    Object.assign(this.projectModel, {"__meta__": {"location": projectLocation}});
    this._setCurrentProject();

    const evtName = Events.gestures.CLOSE_EDITOR;
    this.messageBus.emit(evtName, new UiEvent(evtName, {
      "node": this,
    }));
  }

  _whenProjectModel(projectModel) {
    this._setCurrentProject();
  }

  _whenMessageBus(messageBus) {
    this._setCurrentProject();
  }

  _setCurrentProject() {
    if (!this.messageBus || !this.projectModel) {
      return;
    }

    const evtName = Events.models.SET_CURRENT_PROJECT;
    this.messageBus.emit(evtName, new ModelEvent(evtName, {
      "model": this.projectModel,
    }));
  }
}

window.customElements.define(ConfigurationProjectDetails.is, ConfigurationProjectDetails);
