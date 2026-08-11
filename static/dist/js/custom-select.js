document.addEventListener("DOMContentLoaded", () => {
  let sequence = 0;

  const getLabel = (select) => {
    const label = [...document.querySelectorAll("label")].find(
      (candidate) => candidate.htmlFor === select.id,
    );
    if (!label) return { element: null, text: select.name || "Select" };

    if (!label.id) {
      sequence += 1;
      label.id = `custom-select-label-${sequence}`;
    }
    return { element: label, text: label.textContent.trim() };
  };

  document.querySelectorAll("select").forEach((select) => {
    if (select.dataset.customSelectReady === "true" || select.disabled) return;

    const { element: label, text: labelText } = getLabel(select);
    const isMultiple = select.multiple;
    const root = document.createElement("div");
    const list = document.createElement("div");
    const trigger = document.createElement("button");
    const triggerText = document.createElement("span");
    const chevron = document.createElement("span");
    const darkSurface = select.closest(".brand-masthead, .site-nav, .editorial-footer");

    sequence += 1;
    const listId = `custom-select-list-${sequence}`;
    root.className = `custom-select${darkSurface ? " custom-select--dark" : ""}`;
    list.className = "custom-select__list";
    list.id = listId;
    list.hidden = true;
    list.setAttribute("role", "listbox");
    if (isMultiple) list.setAttribute("aria-multiselectable", "true");

    trigger.className = "custom-select__trigger";
    trigger.type = "button";
    trigger.setAttribute("role", "combobox");
    trigger.setAttribute("aria-controls", listId);
    trigger.setAttribute("aria-expanded", "false");
    trigger.setAttribute("aria-haspopup", "listbox");
    if (label) trigger.setAttribute("aria-labelledby", label.id);
    else trigger.setAttribute("aria-label", labelText);
    if (select.required) trigger.setAttribute("aria-required", "true");

    triggerText.className = "custom-select__trigger-text";
    chevron.className = "custom-select__chevron";
    chevron.setAttribute("aria-hidden", "true");
    trigger.append(triggerText, chevron);

    select.before(root);
    root.append(select, trigger, list);
    select.classList.add("custom-select__native");
    select.dataset.customSelectReady = "true";
    select.tabIndex = -1;
    select.setAttribute("aria-hidden", "true");

    let activeIndex = 0;
    let optionButtons = [];

    const enabledIndexes = () => optionButtons
      .map((button, index) => (button.disabled ? null : index))
      .filter((index) => index !== null);

    const updateTrigger = () => {
      const selected = [...select.options].filter((option) => option.selected);
      if (!selected.length) {
        triggerText.textContent = labelText;
      } else {
        triggerText.textContent = selected.map((option) => option.text).join(", ");
      }
    };

    const sync = () => {
      optionButtons.forEach((button, index) => {
        const option = select.options[index];
        const isSelected = option.selected;
        button.setAttribute("aria-selected", String(isSelected));
        button.classList.toggle("is-selected", isSelected);
      });
      const selectedIndex = [...select.options].findIndex((option) => option.selected && !option.disabled);
      if (selectedIndex >= 0) activeIndex = selectedIndex;
      updateTrigger();
    };

    const close = (restoreFocus = false) => {
      list.hidden = true;
      root.classList.remove("is-open");
      trigger.setAttribute("aria-expanded", "false");
      if (restoreFocus) trigger.focus();
    };

    const open = () => {
      list.hidden = false;
      root.classList.add("is-open");
      trigger.setAttribute("aria-expanded", "true");
    };

    const focusIndex = (index) => {
      const enabled = enabledIndexes();
      if (!enabled.length) return;
      const current = enabled.indexOf(index);
      activeIndex = enabled[current >= 0 ? current : 0];
      optionButtons[activeIndex].focus();
    };

    const move = (direction) => {
      const enabled = enabledIndexes();
      if (!enabled.length) return;
      const current = Math.max(enabled.indexOf(activeIndex), 0);
      const next = (current + direction + enabled.length) % enabled.length;
      activeIndex = enabled[next];
      optionButtons[activeIndex].focus();
    };

    const selectOption = (index) => {
      const option = select.options[index];
      if (!option || option.disabled) return;

      if (isMultiple) option.selected = !option.selected;
      else {
        [...select.options].forEach((candidate, candidateIndex) => {
          candidate.selected = candidateIndex === index;
        });
      }

      select.dispatchEvent(new Event("input", { bubbles: true }));
      select.dispatchEvent(new Event("change", { bubbles: true }));
      sync();
      if (!isMultiple) close(true);
    };

    [...select.options].forEach((option, index) => {
      const optionButton = document.createElement("button");
      const optionText = document.createElement("span");
      const optionMark = document.createElement("span");

      optionButton.className = "custom-select__option";
      optionButton.type = "button";
      optionButton.setAttribute("role", "option");
      optionButton.setAttribute("aria-selected", String(option.selected));
      optionButton.disabled = option.disabled;
      optionButton.tabIndex = -1;
      optionText.className = "custom-select__option-text";
      optionText.textContent = option.text;
      optionMark.className = "custom-select__option-mark";
      optionMark.setAttribute("aria-hidden", "true");
      optionMark.textContent = "✓";
      optionButton.append(optionText, optionMark);
      optionButton.addEventListener("click", () => selectOption(index));
      optionButton.addEventListener("keydown", (event) => {
        if (event.key === "ArrowDown") {
          event.preventDefault();
          move(1);
        } else if (event.key === "ArrowUp") {
          event.preventDefault();
          move(-1);
        } else if (event.key === "Home") {
          event.preventDefault();
          focusIndex(enabledIndexes()[0]);
        } else if (event.key === "End") {
          event.preventDefault();
          const enabled = enabledIndexes();
          focusIndex(enabled[enabled.length - 1]);
        } else if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          selectOption(index);
        } else if (event.key === "Escape") {
          event.preventDefault();
          close(true);
        } else if (event.key === "Tab") {
          close();
        }
      });
      list.append(optionButton);
      optionButtons.push(optionButton);
    });

    trigger.addEventListener("click", () => {
      if (list.hidden) open();
      else close();
    });
    trigger.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        open();
        move(event.key === "ArrowDown" ? 1 : -1);
      } else if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        if (list.hidden) open();
        else close();
      } else if (event.key === "Escape") {
        event.preventDefault();
        close();
      }
    });

    document.addEventListener("pointerdown", (event) => {
      if (!root.contains(event.target)) close();
    });
    select.addEventListener("change", sync);
    if (select.dataset.submitOnChange === "true") {
      select.addEventListener("change", () => select.form?.requestSubmit());
    }
    select.form?.addEventListener("reset", () => window.setTimeout(sync, 0));
    sync();
  });
});
