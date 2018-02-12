"use strict";

import {Events, ModelEvent} from "./events/events.js";
import GesturesManager from "./rendering/gestures-manager.js";
import MessageBus from "./events/message-bus.js";
import Renderer from "./rendering/renderer.js";
import SceneGraph from "./rendering/scene-graph.js";

import EditorUIFactory from "./editor/editor-ui-factory.js";

import Api from "./rendering/shapes/api.js";
import Project from "./rendering/shapes/project.js";

export default class ConfigurationProjectsWebGl extends Polymer.Element {
  static get is() { return "configuration-projects-webgl"; }

  static get properties() {
    return {
      projectModel: {
        type: Object,
        notify: true,
        value: {},
      },
    };
  }

  constructor() {
    super();

    this._editorFactory = new EditorUIFactory(this);
    this._messageBus = new MessageBus();
    this._deleteHandlers = [
      [Api, (evt) => this._deleteApi(evt)],
      [Project, (evt) => this._deleteProject(evt)],
    ];
    this._deleteHandlerFallback = (evt) => this._deleteNodeFallback(evt);
    this.projectModel = undefined;

    this._supportedNodes = {
      "project": {
        "shape": Project,
        "background": [0, 128, 255],
        "getShape": function() {
          const shape = new this.shape(0, 0, 500, 300, this.background, {  // eslint-disable-line new-cap
            "name": "project 1",
            "domain": "www.myproject.com",
          });

          shape.editorUI = self._editorFactory.getEditor(this.shape);
          shape.editorUI.restore({
            "messageBus": self._messageBus,
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
                                       {"path": "<your api>"});

          shape.editorUI = self._editorFactory.getEditor(this.shape);
          shape.editorUI.restore({
            "messageBus": self._messageBus,
            "model": shape.model,
          });

          return shape;
        },
      },
    };

    this._sceneGraph = new SceneGraph(this._messageBus);
    this._wireEvents();
  }

  ready() {
    super.ready();

    this._canvas = this.$.projectsCanvas;

    this._renderer = new Renderer(this._canvas, this._sceneGraph);
    this._renderer.render();

    this._gesturesManager = new GesturesManager(this._canvas, this._sceneGraph, this._messageBus);
    this._gesturesManager.init();
  }

  _addNode(evt) {
    const nodeType = evt.target.getAttribute("data-item-type");
    const desc = this._supportedNodes[nodeType];

    if (!desc) {
      throw new Error(`Node ${nodeType} is not currently supported.`);
    }

    const shape = desc.getShape();
    shape.setPosition(0, 0);

    this._sceneGraph.addNode(shape);
    Events.invalidateSceneGraph(this._sceneGraph);
  }

  _deleteProject(evt) {
    // TODO (rcosnita) Add prompt support before actually deleting a project.
    this._deleteHandlerFallback(evt);
  }

  _deleteApi(evt) {
    // TODO (rcosnita) Add prompt support before actually deleting an api.
    this._deleteHandlerFallback(evt);
  }

  _deleteNodeFallback(evt) {
    const sceneGraph = evt.sceneGraph;

    sceneGraph.deselect();
    sceneGraph.removeNode(evt.node);
    Events.invalidateSceneGraph(this._sceneGraph);
  }

  _removeNode(evt) {
    let handler = this._deleteHandlers.filter((t) => evt.node instanceof t[0])
                                      .map((t) => t[1]);

    handler = handler.length === 0 ? this._deleteHandlerFallback : handler[0];
    handler(evt);
  }

  _wireEvents() {
    this._messageBus.on(Events.gestures.DELETE_NODE, (evt) => this._removeNode(evt));

    const evtProjectSet = Events.models.SET_CURRENT_PROJECT;
    this._messageBus.on(evtProjectSet, (evt) => {
      this.projectModel = evt.model;
    });

    const evtProjectGet = Events.models.GET_CURRENT_PROJECT_LOADED;
    this._messageBus.on(Events.models.GET_CURRENT_PROJECT, (evt) => {
      // TODO (rcosnita) find a better way to prevent get current project errors ...
      if (!this.projectModel) {
        throw new Error("No project available ....");
      }

      this._messageBus.emit(evtProjectGet, new ModelEvent(evtProjectGet, {
        "model": this.projectModel,
      }));
    });
  }
}

window.customElements.define(ConfigurationProjectsWebGl.is, ConfigurationProjectsWebGl);
