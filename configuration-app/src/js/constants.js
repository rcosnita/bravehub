if (!window.Bravehub) {
  window.Bravehub = {};
}

if (!window.Bravehub.Constants) {
  window.Bravehub.Constants = (function() {
    const BASE_URL = "http://configuration-api.api.bravehub-dev.com";
    const PROJECTS_URL = `${BASE_URL}/v0.1/projects`;

    return {
      BASE_URL: BASE_URL,
      PROJECTS_URL: PROJECTS_URL,
    };
  })();
}
