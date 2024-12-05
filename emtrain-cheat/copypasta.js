const sleep = (ms) => {
    console.log(`sleeping ${ms} milliseconds`);
    return new Promise(resolve => setTimeout(resolve, ms));
};

const simulateClick = (element) => {
    const clickEvent = new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
        view: window
    });
    element.dispatchEvent(clickEvent);
};

const simulateKeyPress = (element, key) => {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype,
        'value'
    ).set;
    nativeInputValueSetter.call(element, element.value + key);

    const inputEvent = new Event('input', { bubbles: true });
    element.dispatchEvent(inputEvent);
};

const click = (name, element) => {
    if (!element) {
        return false;
    }

    console.log(`click ${name}`);
    simulateClick(element);

    return true;
};

const fill = (name, element) => {
    if (!element) {
        return false;
    }

    console.log(`fill ${name}`);
    element.value = 'no comments';
    simulateKeyPress(element, '.');

    return true;
};

const main = async () => {
    sleep(1000);

    while (true) {
        const playVideoClicked = click('playVideo', document.querySelector('[aria-label="Play video"]'));
        if (playVideoClicked) {
            await sleep(120000);
        }

        const yellowStressfulClicked = click('yellowStressful', document.querySelector('[aria-label="Yellow - Stressful. Use the left or right arrow key only to select a color."]'));
        if (yellowStressfulClicked) {
            await sleep(1000);
            click('submit', document.querySelector('[data-cy="submit"]'));
            await sleep(1000);
        }

        const viewDocumentClicked = click('viewDocument', document.querySelector('[data-cy="viewDocument"]'));
        if (viewDocumentClicked) {
            await sleep(1000);
            click('review', document.querySelector('[data-cy="review"]'));
        }

        const freeformTextFilled = fill('freeformText', document.querySelector('[data-cy="freeformText"]'));
        if (freeformTextFilled) {
            await sleep(1000);
            click('submit', document.querySelector('[data-cy="submit"]'));
            await sleep(1000);
        }

        const neutralDontKnowClicked = click('neutralDontKnow', document.querySelector('[aria-label="Neutral / Don’t Know "]'));
        if (neutralDontKnowClicked) {
            await sleep(1000);
            click('submit', document.querySelector('[data-cy="submit"]'));
            await sleep(1000);
        } else {
            const choice0Clicked = click('choice0', document.querySelector('[data-cy="Choice-0"]'));
            if (choice0Clicked) {
                await sleep(1000);
                click('submit', document.querySelector('[data-cy="submit"]'));
                await sleep(1000);
                click('choice1', document.querySelector('[data-cy="Choice-1"]'));
                await sleep(1000);
                click('submit', document.querySelector('[data-cy="submit"]'));
                await sleep(1000);
                click('choice2', document.querySelector('[data-cy="Choice-2"]'));
                await sleep(1000);
                click('submit', document.querySelector('[data-cy="submit"]'));
                await sleep(1000);
            }
        }

        click('nextLessonCardButton', document.getElementById('next_lesson_card_button'));
        await sleep(5000);
    }
};

await main();
