/* @emdad-module */

import { HIGHLIGHT_CLASS, searchHighlight } from "@mail/core/common/message_search_hook";
import { triggerHotkey } from "@web/../tests/helpers/utils";
import { click, contains, insertText } from "@web/../tests/utils";
import { startServer } from "@bus/../tests/helpers/mock_python_environment";
import { start } from "../helpers/test_utils";
import { SIZES, patchUiSize } from "../helpers/patch_ui_size";

QUnit.module("Search highlight test", {});

QUnit.test("Search highlight", async (assert) => {
    const testCases = [
        {
            input: "test emdad",
            output: `test <span class="${HIGHLIGHT_CLASS}">emdad</span>`,
            searchTerm: "emdad",
        },
        {
            input: '<a href="https://www.emdad.com">https://www.emdad.com</a>',
            output: `<a href="https://www.emdad.com">https://www.<span class="${HIGHLIGHT_CLASS}">emdad</span>.com</a>`,
            searchTerm: "emdad",
        },
        {
            input: '<a href="https://www.emdad.com">emdad</a>',
            output: `<a href="https://www.emdad.com"><span class="${HIGHLIGHT_CLASS}">emdad</span></a>`,
            searchTerm: "emdad",
        },
        {
            input: '<a href="https://www.emdad.com">emdad</a> emdad is a free software',
            output: `<a href="https://www.emdad.com"><span class="${HIGHLIGHT_CLASS}">emdad</span></a> <span class="${HIGHLIGHT_CLASS}">emdad</span> is a free software`,
            searchTerm: "emdad",
        },
        {
            input: "emdad is a free software",
            output: `<span class="${HIGHLIGHT_CLASS}">emdad</span> is a free software`,
            searchTerm: "emdad",
        },
        {
            input: "software emdad is a free",
            output: `software <span class="${HIGHLIGHT_CLASS}">emdad</span> is a free`,
            searchTerm: "emdad",
        },
        {
            input: `<ul>
                <li>emdad</li>
                <li><a href="https://emdad.com">emdad ERP</a> Best ERP</li>
            </ul>`,
            output: `<ul>
                <li><span class="${HIGHLIGHT_CLASS}">emdad</span></li>
                <li><a href="https://emdad.com"><span class="${HIGHLIGHT_CLASS}">emdad</span> ERP</a> Best ERP</li>
            </ul>`,
            searchTerm: "emdad",
        },
        {
            input: "test <strong>emdad</strong> test",
            output: `<span class="${HIGHLIGHT_CLASS}">test</span> <strong><span class="${HIGHLIGHT_CLASS}">emdad</span></strong> <span class="${HIGHLIGHT_CLASS}">test</span>`,
            searchTerm: "emdad test",
        },
        {
            input: "test <br> test",
            output: `<span class="${HIGHLIGHT_CLASS}">test</span> <br> <span class="${HIGHLIGHT_CLASS}">test</span>`,
            searchTerm: "emdad test",
        },
        {
            input: "<strong>test</strong> test",
            output: `<strong><span class="${HIGHLIGHT_CLASS}">test</span></strong> <span class="${HIGHLIGHT_CLASS}">test</span>`,
            searchTerm: "test",
        },
        {
            input: "<strong>a</strong> test",
            output: `<strong><span class="${HIGHLIGHT_CLASS}">a</span></strong> <span class="${HIGHLIGHT_CLASS}">test</span>`,
            searchTerm: "a test",
        },
        {
            input: "&amp;amp;",
            output: `<span class="${HIGHLIGHT_CLASS}">&amp;amp;</span>`,
            searchTerm: "&amp;",
        },
        {
            input: "&amp;amp;",
            output: `<span class="${HIGHLIGHT_CLASS}">&amp;</span>amp;`,
            searchTerm: "&",
        },
        {
            input: "<strong>test</strong> hello",
            output: `<strong><span class="${HIGHLIGHT_CLASS}">test</span></strong> <span class="${HIGHLIGHT_CLASS}">hello</span>`,
            searchTerm: "test hello",
        },
        {
            input: "<p>&lt;strong&gt;test&lt;/strong&gt; hello</p>",
            output: `<p>&lt;strong&gt;<span class="${HIGHLIGHT_CLASS}">test</span>&lt;/strong&gt; <span class="${HIGHLIGHT_CLASS}">hello</span></p>`,
            searchTerm: "test hello",
        },
    ];
    for (const { input, output, searchTerm } of testCases) {
        assert.equal(searchHighlight(searchTerm, input), output);
    }
});

QUnit.test("Display highligthed search in chatter", async () => {
    patchUiSize({ size: SIZES.XXL });
    const pyEnv = await startServer();
    const partnerId = pyEnv["res.partner"].create({ name: "John Doe" });
    pyEnv["mail.message"].create({
        body: "not empty",
        model: "res.partner",
        res_id: partnerId,
    });
    const { openFormView } = await start();
    await openFormView("res.partner", partnerId);
    await click("[title='Search Messages']");
    await insertText(".o_searchview_input", "empty");
    triggerHotkey("Enter");
    await contains(`.o-mail-Chatter-search .o-mail-Message span.${HIGHLIGHT_CLASS}`);
});

QUnit.test("Display multiple highligthed search in chatter", async () => {
    patchUiSize({ size: SIZES.XXL });
    const pyEnv = await startServer();
    const partnerId = pyEnv["res.partner"].create({ name: "John Doe" });
    pyEnv["mail.message"].create({
        body: "not test empty",
        model: "res.partner",
        res_id: partnerId,
    });
    const { openFormView } = await start();
    await openFormView("res.partner", partnerId);
    await click("[title='Search Messages']");
    await insertText(".o_searchview_input", "not empty");
    triggerHotkey("Enter");
    await contains(`.o-mail-Chatter-search .o-mail-Message span.${HIGHLIGHT_CLASS}`, { count: 2 });
});

QUnit.test("Display highligthed search in Discuss", async () => {
    const pyEnv = await startServer();
    const channelId = pyEnv["discuss.channel"].create({ name: "General" });
    pyEnv["mail.message"].create({
        author_id: pyEnv.currentPartnerId,
        body: "not empty",
        attachment_ids: [],
        message_type: "comment",
        model: "discuss.channel",
        res_id: channelId,
    });
    const { openDiscuss } = await start();
    await openDiscuss(channelId);
    await click("button[title='Search Messages']");
    await insertText(".o_searchview_input", "empty");
    triggerHotkey("Enter");
    await contains(`.o-mail-SearchMessagesPanel .o-mail-Message span.${HIGHLIGHT_CLASS}`);
});

QUnit.test("Display multiple highligthed search in Discuss", async () => {
    const pyEnv = await startServer();
    const channelId = pyEnv["discuss.channel"].create({ name: "General" });
    pyEnv["mail.message"].create({
        author_id: pyEnv.currentPartnerId,
        body: "not prout empty",
        attachment_ids: [],
        message_type: "comment",
        model: "discuss.channel",
        res_id: channelId,
    });
    const { openDiscuss } = await start();
    await openDiscuss(channelId);
    await click("button[title='Search Messages']");
    await insertText(".o_searchview_input", "not empty");
    triggerHotkey("Enter");
    await contains(`.o-mail-SearchMessagesPanel .o-mail-Message span.${HIGHLIGHT_CLASS}`, {
        count: 2,
    });
});

QUnit.test("Display highligthed with escaped character must ignore them", async () => {
    patchUiSize({ size: SIZES.XXL });
    const pyEnv = await startServer();
    const partnerId = pyEnv["res.partner"].create({ name: "John Doe" });
    pyEnv["mail.message"].create({
        body: "<p>&lt;strong&gt;test&lt;/strong&gt; hello</p>",
        model: "res.partner",
        res_id: partnerId,
    });
    const { openFormView } = await start();
    await openFormView("res.partner", partnerId);
    await click("[title='Search Messages']");
    await insertText(".o_searchview_input", "test hello");
    triggerHotkey("Enter");
    await contains(`.o-mail-Chatter-search .o-mail-Message span.${HIGHLIGHT_CLASS}`, { count: 2 });
    await contains(`.o-mail-Message-body`, { text: "<strong>test</strong> hello" });
});
