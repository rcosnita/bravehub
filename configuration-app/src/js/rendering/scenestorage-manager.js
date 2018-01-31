"use strict";

import Events from "../events/events.js";

/**
 * StorageManager provides the layer which hooks a scenegraph storage into the application.
 * The save operations are done out of band and only when the scenegraph is not dirty. We do this
 * in order to avoid overlapping with rendering cycles which might introduce performance penalties.
 *
 * All actions taken by the scene storage manager are also transmitted on a given message bus.
 * This will help us implement UI elements like autosaved / not saved scene.
 */
export default class SceneStorageManager {
  constructor(sceneStorage, scene, messageBus) {
    this._messageBus = messageBus;
    this._sceneStorage = sceneStorage;
    this._scene = scene;
    this._intervalSave = undefined;
    this._intervalSavePeriod = window.Bravehub.Constants.SCENEGRAPH_SAVE_INTERVAL;
  }

  init() {
    this._wireEvents();
  }

  get scene() {
    return this._scene;
  }

  /**
   * Loads the given scene from the persistent storage and populates the scenegraph with the right shapes.
   *
   * @param {UUID} sceneId The unique identifier of the scene we want to restore.
   * @param {Object} supportedNodes The nodes factory which can be used for retrieving shapes.
   * @returns {Promise} a promise which resolves to the scene project or rejects with a specific error.
   */
  loadScene(sceneId, supportedNodes) {
    return new Promise((resolve, reject) => {
      this._sceneStorage.load(sceneId).then((data) => {
        this._restoreScene(data, supportedNodes, resolve, reject);
      });
    });
  }

  _restoreScene(data, supportedNodes, resolve) {
    data.shapes.forEach((shape) => {
      const nodeType = shape.type;
      const desc = supportedNodes[nodeType];

      if (!desc) {
        throw new Error(`Node ${nodeType} is not currently supported.`);
      }

      const node = desc.getShape();
      const d = shape.coordinates.D;
      const cost = shape.coordinates.cost;
      const sint = shape.coordinates.sint;
      const scaleFactor = window.devicePixelRatio / shape.screen.density;

      const x = d * sint * scaleFactor;
      const y = d * cost * scaleFactor;
      node.setPosition(x, y);

      const loader = node.model.fetch(shape.model);
      if (nodeType === "project") {
        loader.then((projectModel) => {
          resolve(projectModel);
        });
      }

      this._scene.addNode(node);
    });

    this._scene.dirty = true;
  }

  _saveScene() {
    if (this._scene.isDirty) {
      return;
    }

    this._sceneBody = this._toSceneApiBody();
    if (!this._sceneBody.id) {
      return;
    }

    this._sceneStorage.save(this._sceneBody.id, this._sceneBody);

    clearInterval(this._intervalSave);
    this._intervalSave = undefined;
  }

  _toSceneApiBody() {
    const sceneBody = {
      "id": undefined,
      "shapes": [],
    };

    this._scene.nodes
      .filter((node) => node.type === "project" || node.type === "api")
      .forEach((node) => {
        const x = node.x;
        const y = node.y;

        let d = x === 0 && y === 0 ? 0 : Math.sqrt(x ^ 2 + y ^ 2);
        let cost = d === 0 ? 1 : y / d;
        let sint = d === 0 ? 0 : x / d;

        const sceneNode = {
          "type": node.type,
          "coordinates": {
            "D": d,
            "cost": cost,
            "sint": sint,
          },
          "model": {
            "id": node.model.id,
          },
          "screen": {
            "density": window.devicePixelRatio,
          },
        };

        // This causes memory displacement but helps us conserve z-index correctly.
        sceneBody.shapes.splice(0, 0, sceneNode);

        if (node.type === "project") {
          sceneBody.id = node.model.id;
        }
      });

    if (sceneBody.id) {
      sceneBody.shapes
        .filter((node) => node.type === "api")
        .forEach((node) => {
          node.model.projectId = sceneBody.id;
        });
    }

    return sceneBody;
  }

  _wireEvents() {
    this._messageBus.on(Events.sceneGraph.INVALIDATE_SCENE, () => {
      if (this._intervalSave) {
        return;
      }

      this._intervalSave = setInterval(() => this._saveScene(), this._intervalSavePeriod);

      this._messageBus.on(Events.sceneGraph.NEW_SCENE, () => {
        window.clearInterval(this._intervalSave);
      });
    });
  }
}
