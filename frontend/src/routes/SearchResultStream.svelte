<script>
    import { onMount } from "svelte";
    import { fly } from "svelte/transition";

    /**
     * @type {{ url: string; name: string; snippet: string; }}
     */
    export let search;

    export let message = "";

    export let exeGPT = false;

    export let query = "";

    export let searchEnglish = false;

    let exceedToken = false;

    let loading = false;

    let advice = "";

    let displayedAdvice = "";
    let isStreaming = false;
    let isWriting = false;

    async function callChatGPT() {
        try {
            if (!exeGPT) return;

            loading = true;
            isStreaming = false;

            advice = "";
            displayedAdvice = "";

            const send_message = {
                content: message,
                url: search.url,
                name: search.name,
                query: query,
                searchEnglish: searchEnglish,
                forceExecute: exceedToken,
            };

            const response = await fetch("/yourwebcopilot/getadvicews", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(send_message),
            });

            advice = "";
            displayedAdvice = "";
            loading = false;
            exceedToken = false;
            isStreaming = true;

            if (response.body) {
                const decoder = new TextDecoder();
                const reader = response.body.getReader();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) {
                        break;
                    }
                    const text = decoder.decode(value);
                    advice += text;

                    isWriting = true;
                    await delayAndNewContent(text)
                    isWriting = false;
                }
            }

            // adviceが"!ページ情報のトークン数が規定値を超えている"から始まっている場合のif文を追加
            if (advice.startsWith("!ページ情報のトークン数が規定値")) {
                exceedToken = true;
            } else {
                exceedToken = false;
            }
        } catch (error) {
            console.error(error);
        } finally {
            loading = false;
            isStreaming = false;
            isWriting = false;
        }
    }

    async function executeGPTprocess() {
        exeGPT = true;
        callChatGPT();
    }

    /**
     * @param {string} content 
     */
    async function delayAndNewContent(content) {
        await new Promise(resolve => setTimeout(() => {
            displayedAdvice += content;
            resolve(null);
        }, 33));
    }

    onMount(() => {
        callChatGPT();
    });
</script>

<div transition:fly={{ y: 50, duration: 500 }}>
    <a href={search.url} target="_blank" class="bing_link">{search.name}</a>
    <p class="snippet">
        {search.snippet}
    </p>
</div>
{#if exeGPT}
    {#if loading}
        <div class="loader"></div>
    {:else}
        <div class="chat_assistant" transition:fly={{ y: 50, duration: 500 }}>
            <pre class="chat_message">{displayedAdvice}</pre>
            {#if exceedToken}
                <button
                    class="button_class button_red"
                    on:click={executeGPTprocess}>それでも確認する</button
                >
            {:else}
                {#if isStreaming && isWriting}
                    <span class="streaming_fast"></span>
                {:else if isStreaming && !isWriting}
                    <span class="streaming"></span>
                {:else if !isStreaming && isWriting}
                    <span class="streaming_fast"></span>
                {/if}
            {/if}
        </div>
    {/if}
{:else}
    <div class="button_field" transition:fly={{ y: 50, duration: 500 }}>
        <button class="button_class" on:click={executeGPTprocess}
            >GPTで確認する</button
        >
    </div>
{/if}

<style>
    .bing_link {
        font-size: 0.9em;
    }
    .snippet {
        font-size: 0.8em;
        margin: 0px;
    }

    .button_field {
        width: 100%;
        text-align: center;
        margin: 20px auto;
    }

    .button_class {
        width: 200px;
        background-color: #99f;
        color: #fff;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        font-weight: bold;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 10px;
    }

    .button_red {
        background-color: #f99;
    }
    .chat_assistant {
        width: 90%;
        min-height: 50px;
        border: 1px solid #ccc;
        background-color: #fff;
        margin-left: auto;
        padding: 5px 5px 5px 10px;
        margin: 10px 30px 20px auto;
        border-radius: 10px 10px 0 10px;
        box-shadow: 1px 2px 2px 0px #ccc;
    }

    .chat_message {
        white-space: pre-wrap;
        font-size: 0.9em;
        font-family: "Noto Sans JP", sans-serif;
    }

    .loader {
        margin: auto;
        margin-top: 10px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        border: 5px solid #ccc;
        border-top-color: #333;
        animation: spin 1s linear infinite;
    }

    .streaming {
        display: inline-block;
        vertical-align: middle; 
        font-size: 1em; /* 1文字分の大きさ */
        width: 1em;
        height: 1em;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #66f;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin:auto;
    }

    .streaming_fast {
        display: inline-block;
        vertical-align: middle; 
        font-size: 1em; /* 1文字分の大きさ */
        width: 1em;
        height: 1em;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #66f;
        border-radius: 50%;
        animation: spin 0.1s linear infinite;
        margin:auto;
    }

    @keyframes spin {
        from {
            transform: rotate(0deg);
        }

        to {
            transform: rotate(360deg);
        }
    }
</style>
