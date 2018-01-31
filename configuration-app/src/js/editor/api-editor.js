"use strict";

import Editor from "./editor.js";
import {Events, ModelEvent} from "../events/events.js";

export default class ApiEditor extends Editor {
  constructor(opts) {
    super();
    this._component = undefined;
    this._createApiComponent();
  }

  get domElement() { return this._component; }

  restore(opts) {
    const model = opts.model;

    this._component.apiModel = { };
    this._component.apiModel = model;
    this._component.messageBus = opts.messageBus;

    this._fetchCurrentProject(opts.messageBus);
  }

  _createApiComponent() {
    this._component = document.createElement("configuration-api-details");
    this._component.style.width = "300px";
    this._component.style.height = "300px";
    this._component.style.visibility = "hidden";
    this._component.style.position = "absolute";
    this._component.apiModel = { };
  }

  _fetchCurrentProject(messageBus) {
    const evtName = Events.models.GET_CURRENT_PROJECT;
    const evtNameResponse = Events.models.GET_CURRENT_PROJECT_LOADED;

    messageBus.on(evtNameResponse, (evt) => {
      this._component.projectModel = evt.model;
    });

    messageBus.emit(evtName, new ModelEvent(evtName));
  }
}
