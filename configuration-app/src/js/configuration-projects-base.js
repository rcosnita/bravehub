"use strict";

import {Events, ModelEvent} from "./events/events.js";
import GesturesManager from "./rendering/gestures-manager.js";
import MessageBus from "./events/message-bus.js";
import Renderer from "./rendering/renderer.js";
import SceneGraph from "./rendering/scene-graph.js";
import SceneGraphStorage from "./rendering/scenegraph-storage.js";
import SceneStorageManager from "./rendering/scenestorage-manager.js";

import EditorUIFactory from "./editor/editor-ui-factory.js";

import Api from "./rendering/shapes/api.js";
import Project from "./rendering/shapes/project.js";

import SupportedNodesManager from "./rendering/supportednodes-manager.js";

export default class ConfigurationProjectsBase extends Polymer.Element {
  constructor() {
    super();

    this._constants = window.Bravehub.Constants;
    this._editorFactory = new EditorUIFactory(this);
    this._messageBus = new MessageBus();
    this._deleteHandlers = [
      [Api, (evt) => this._deleteApi(evt)],
      [Project, (evt) => this._deleteProject(evt)],
    ];
    this._deleteHandlerFallback = (evt) => this._deleteNodeFallback(evt);
    this.projectModel = undefined;

    this._supportedNodes = SupportedNodesManager.getSupported(this._editorFactory, this._messageBus);

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

    this._sceneStorageManager = new SceneStorageManager(new SceneGraphStorage(), this._sceneGraph, this._messageBus);
    this._sceneStorageManager.init();
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
      if (!this.projectModel) {
        return;
      }

      this._messageBus.emit(evtProjectGet, new ModelEvent(evtProjectGet, {
        "model": this.projectModel,
      }));
    });
  }
}
