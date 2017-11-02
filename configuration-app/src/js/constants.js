if (!window.Bravehub) {
  window.Bravehub = {};
}

if (!window.Bravehub.Constants) {
  window.Bravehub.Constants = (function() {
    const BASE_URL = "http://localhost:5000";
    const PROJECTS_URL = `${BASE_URL}/v0.1/projects`;

    return {
      BASE_URL: BASE_URL,
      PROJECTS_URL: PROJECTS_URL,
    };
  })();
}
