import assert from "node:assert/strict";
import test from "node:test";

import { HomeCarouselController } from "../../static/src/js/home-carousel-controller.mjs";

const createElement = () => ({
  attributes: new Map(),
  inert: false,
  style: {},
  textContent: "",
  setAttribute(name, value) { this.attributes.set(name, value); },
});

const createCarousel = (count) => {
  const track = createElement();
  const indexElement = createElement();
  const slides = Array.from({ length: count }, createElement);
  return { controller: new HomeCarouselController({ track, slides, indexElement }), track, slides, indexElement };
};

test("starts on slide 0 and synchronizes the track and accessibility state", () => {
  const { controller, track, slides, indexElement } = createCarousel(3);

  assert.equal(controller.goTo(0), 0);
  assert.equal(track.style.transform, "translateX(-0%)");
  assert.equal(indexElement.textContent, "01");
  assert.equal(slides[0].inert, false);
  assert.equal(slides[1].inert, true);
  assert.equal(slides[1].attributes.get("aria-hidden"), "true");
});

test("navigates next and previous between slides", () => {
  const { controller, track, slides, indexElement } = createCarousel(3);

  controller.goTo(0);
  assert.equal(controller.next(), 1);
  assert.equal(track.style.transform, "translateX(-100%)");
  assert.equal(indexElement.textContent, "02");
  assert.equal(controller.next(), 2);
  assert.equal(track.style.transform, "translateX(-200%)");
  assert.equal(controller.previous(), 1);
  assert.equal(slides[1].inert, false);
});

test("wraps from the last slide to the first and back", () => {
  const { controller } = createCarousel(3);

  controller.goTo(2);
  assert.equal(controller.next(), 0);
  assert.equal(controller.previous(), 2);
});

test("a single slide remains stable", () => {
  const { controller, track, slides, indexElement } = createCarousel(1);

  assert.equal(controller.goTo(0), 0);
  assert.equal(controller.next(), 0);
  assert.equal(controller.previous(), 0);
  assert.equal(track.style.transform, "translateX(-0%)");
  assert.equal(indexElement.textContent, "01");
  assert.equal(slides[0].inert, false);
});
