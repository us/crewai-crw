# Changelog

## [0.5.0](https://github.com/us/crewai-crw/compare/v0.4.0...v0.5.0) (2026-04-09)


### Features

* add integration tests and CI for fastcrw.com ([#7](https://github.com/us/crewai-crw/issues/7)) ([0027561](https://github.com/us/crewai-crw/commit/0027561bd7b8a3a430308feb70660f743f7c2b25))


### Bug Fixes

* bump crw&gt;=0.3.4, enable search and crawl integration tests ([3e4d3e5](https://github.com/us/crewai-crw/commit/3e4d3e5709dfdd047d0e99018c8e50390c5a5dce))
* **ci:** remove --timeout flag from integration test command ([#9](https://github.com/us/crewai-crw/issues/9)) ([9cab5c1](https://github.com/us/crewai-crw/commit/9cab5c16674299717535ba20524f5397a9d3eee1))

## [0.4.0](https://github.com/us/crewai-crw/compare/v0.3.0...v0.4.0) (2026-04-02)


### Features

* add CrwSearchWebTool for web search ([fb2c257](https://github.com/us/crewai-crw/commit/fb2c2570ec011b95d4bc4585c91b11438f028960))

## [0.3.0](https://github.com/us/crewai-crw/compare/v0.2.0...v0.3.0) (2026-03-29)


### Features

* use crw SDK with auto-download binary, no server required ([bfd693a](https://github.com/us/crewai-crw/commit/bfd693ab71798fc3a3ce31eb7c36a1ebf4101a43))


### Bug Fixes

* update test to expect fastcrw.com default ([dabac91](https://github.com/us/crewai-crw/commit/dabac91429d4ff6881fbe5c0080ff3a76c15f785))

## [0.2.0](https://github.com/us/crewai-crw/compare/v0.1.0...v0.2.0) (2026-03-28)


### Features

* change default to fastcrw.com cloud, add 3-tier setup (cloud/binary/docker) ([79e750d](https://github.com/us/crewai-crw/commit/79e750db55bc64bbe08fcc6b6ee02678030aa319))


### Documentation

* add 500 free credits signup CTA ([cebc081](https://github.com/us/crewai-crw/commit/cebc081a0ecdb6ce000ebfb3389e1a9f50a50112))
* reorder README — cloud (fastcrw.com) first, self-hosted second ([5d7f94c](https://github.com/us/crewai-crw/commit/5d7f94cbd122451bc24d19e365ec5973abd88c9a))
* rewrite README with clear self-hosted vs cloud setup sections ([9be2e28](https://github.com/us/crewai-crw/commit/9be2e28121419661c14f58ca649e6fe0f640ea41))

## 0.1.0 (2026-03-27)


### Features

* initial release of crewai-crw package ([8463309](https://github.com/us/crewai-crw/commit/8463309782bf2bc2956a6e915602c817ae402f43))


### Bug Fixes

* **ci:** drop Python 3.10 (onnxruntime requires 3.11+) ([6433976](https://github.com/us/crewai-crw/commit/6433976d4594aac98477f520854f08cbddb719dd))
* update GitHub URLs and improve README with cloud/self-hosted setup ([7b8b234](https://github.com/us/crewai-crw/commit/7b8b234ecd0701c5005c3e6541e17b9ad5884803))


### Documentation

* add PyPI badges, uv install option, and complete agent examples ([c7de6c8](https://github.com/us/crewai-crw/commit/c7de6c837251c9b151b4d514944381118402b845))
