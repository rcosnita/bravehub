if (!window.Bravehub) {
  window.Bravehub = {};
}

if (!window.Bravehub.Constants) {
  window.Bravehub.Constants = (function() {
    const BASE_URL = "localhost:5000";
    const PROJECTS_URL = `http://configuration-api.${BASE_URL}/v0.1/projects`;
    const SCENEGRAPH_URL = `http://scenegraph-api.${BASE_URL}/v0.1/scenes`;

    /**
     * This constant controls how often the scenegraph must be persisted.
     * @const
     */
    const SCENEGRAPH_SAVE_INTERVAL = 1000;

    return {
      BASE_URL: BASE_URL,
      PROJECTS_URL: PROJECTS_URL,
      SCENEGRAPH_URL: SCENEGRAPH_URL,
      SCENEGRAPH_SAVE_INTERVAL: SCENEGRAPH_SAVE_INTERVAL,
    };
  })();
}
