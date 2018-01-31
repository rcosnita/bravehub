"use strict";

/**
 * SceneGraphStorage provides the main api for persisting a scene graph into a permanent storage.
 * Bravehub provides such a microservice for managing a complete scenegraph.
 */
export default class SceneGraphStorage {
  constructor() {
    this._projectsApiUrl = window.Bravehub.Constants.PROJECTS_URL;
    this._scenesApiUrl = window.Bravehub.Constants.SCENEGRAPH_URL;
  }

  /**
   * Load the scenegraph associated with the given project.
   *
   * @param {UUID} projectId project unique identifier.
   * @return {Promise} a promise which resolves to the scenegraph or gets rejected with a specific error.
   */
  load(projectId) {
    const action = Rx.DOM.ajax({  // eslint-disable-line no-undef
      url: `${window.Bravehub.Constants.SCENEGRAPH_URL}/${projectId}`,
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    return new Promise((resolve, reject) => {
      action.subscribe(
        (resp) => resolve(JSON.parse(resp.response)),
        (err) => reject(err)  // eslint-disable-line no-console
      );
    });
  }

  /**
   * Saves the current scene belonging to the specified project. Any previous stored scene is replaced.
   * We only keep the complex nodes in the persisted version because all the rests can be inferred.
   *
   * @param {UUID} projectId project unique identifier.
   * @param {SceneGraph} scene a scene graph object to be stored.
   * @return {none}
   */
  save(projectId, scene) {
    const action = Rx.DOM.ajax({  // eslint-disable-line no-undef
      url: `${window.Bravehub.Constants.SCENEGRAPH_URL}/${projectId}`,
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(scene),
    });

    action.subscribe(
      (resp) => console.log("Scenegraph saved."),
      (err) => console.log(err)  // eslint-disable-line no-console
    );
  }
}
