<script>
    import { fly,scale } from 'svelte/transition';
    import SearchResultStream from './SearchResultStream.svelte';

    let title = "Your Web Copilot"

    /**
     * @type {{ role: string; content: string; query:string; urls:string[]; titles:string[]; bing:any[]}[]}
     */
    export let chats = [];

    let message = "";

    let loading = false;

    let newsite = "";

    let sitelist = ["learn.microsoft.com"]

    let error_message = ""

    const autoGPT_num = 3;

    let searchEnglish = false;

    function toggleSearchEnglish() {
      searchEnglish = !searchEnglish;
    }

    // send POST request to call ChatGPT
    async function postMessage() {

      error_message = "";
      loading = true;

      try{

      chats = [...chats, {"role":"user","content":message,"query":"","urls":[],"titles":[],"bing":[]}]
      const sendmessage = {"content":message,"searchEnglish":searchEnglish,"sitelist":sitelist}
      message = "";

      const response = await fetch("/yourwebcopilot/getbingresult", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(sendmessage)
      });

      const data = await response.json();

      const query = data.query;

      /**
       * @type {{ url: string; title: string; message:string}[]}
       */
      const searchResult = data.searchResult;

      const titles = searchResult.map(({title}) => title);
      const urls = searchResult.map(({url}) => url);
      

      chats = [...chats, {"role":"bing","content":data.message,"query":query, "urls":[], "titles":[], "bing":searchResult}]
//      chats = [...chats, {"role":"assistant","content":data.message,"query":query,"urls":urls,"titles":titles, "bing":[]}]

      }catch(e){
        console.error(e);
        error_message =  "何らかのエラーが発生しました。";
      }finally{
        loading = false;
      }
    }

    /**
     * @param {number} index
     */
    function removeAsite(index){
      sitelist.splice(index, 1);
      sitelist = sitelist;
    }

    // KeyDown EventHandler
    /**
     * @param {{ keyCode: number; shiftKey: any; preventDefault: () => void; }} e
     */
     function handleKeyDown(e) {
        if (e.keyCode === 13 && e.shiftKey) {
          // Shift+Enter
          message += "\n";
          e.preventDefault();
        }else if (e.keyCode === 13) {
          // Enter
          postMessage();
          e.preventDefault();
        }
    }
    
    // Automatic scrolldown in chatfield
    import { afterUpdate } from "svelte";

    const scrollBottom = () => {
      const chatField = document.querySelector(".chatfield");
      if (chatField) {
        const height = chatField.scrollHeight;
        chatField.scrollTo(0, height);
      }
    };
    afterUpdate(scrollBottom);
</script>

<svelte:head>
  <title>{title}</title>
</svelte:head>

<div class="main">
  <div class="horizontal-container-top">
    <h1>{title}</h1>
  <button class="toggle-button" on:click={toggleSearchEnglish}>
    {#if searchEnglish}
      検索は英語モード
    {:else}
      通常モード
    {/if}
  </button>
  </div>

  <div class="horizontal-container">


    <input class="siteoption" type="text" bind:value={newsite} placeholder="サイトを追加" />
    <button class="add-sitebutton" on:click={() => {
      sitelist = [...sitelist, newsite]
      newsite = ""
    }}>+</button>

    {#each sitelist as site, index}
      <div class="sitefield" transition:scale>
        {site}
        <button class="sitebutton" on:click={() => removeAsite(index)}>X</button>
      </div>
    {/each}

  </div>
  <textarea class="messagebox" title="chat" name="chat" id="chat" placeholder="調べたい内容を入力してください" bind:value={message} on:keydown={handleKeyDown}></textarea>
  <div class="messagebox_bottom">
    <button class="button_clear" on:click={() => chats = []}>クリア</button>
    <button class="button_send" on:click={postMessage}>送信</button>
  </div>

  {#if error_message}
    <div class="error">{error_message}</div>
  {/if}

  <div class="chatfield">
      {#each chats as chat}
      {#if chat.role == "bing"}
      <div class="bing_query" transition:fly="{{ y: 50, duration: 500 }}">検索ワード:{chat.query}</div>
        {#each chat.bing.slice(0, autoGPT_num) as search}
        <SearchResultStream {search} message={chat.content} exeGPT={true} query={chat.query} searchEnglish={searchEnglish}/>
        {/each}
        {#each chat.bing.slice(autoGPT_num) as search}
        <SearchResultStream {search} message={chat.content} exeGPT={false} query={chat.query} searchEnglish={searchEnglish}/>
        {/each}
      {/if}
      {#if chat.role == "user"}
      <div class="chat_{chat.role}" transition:fly="{{ y: 50, duration: 500 }}">
        <pre class="chat_message">{chat.content}</pre>
      </div>
      {/if}
    {/each}
    {#if loading}
      <div class="loader"></div>
    {/if}
  </div>

  
</div>

<style>
@import url('https://fonts.googleapis.com/css?family=Noto+Sans+JP:400,700&display=swap');

:global(body){
  --back_color:#f0f0ff;
  --btn_color:#6666ff;
  --chat_color:#444499;
  margin:0px;
  background: linear-gradient(to right top, #f0f0f0, var(--back_color));
  font-family: 'Noto Sans JP', sans-serif;
}

h1{
  text-align: center;
  margin-left:50px;
}

.horizontal-container-top {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: baseline;
  margin: auto;
}

.horizontal-container {
  display: flex;
  flex-direction: row;
  justify-content: left; /* 中央寄せに変更 */
  align-items: center;
}

.siteoption{
  width: 200px;
  margin-left: 30px;
  font-size: 1.0em;
  font-family: 'Noto Sans JP', sans-serif;
  border: 1px solid #666;
  border-radius: 10px;
  padding-left: 10px;
}

.sitefield{
  font-family: 'Noto Sans JP', sans-serif;
  border: none;
  border-radius: 20px;
  background-color: #ccf;
  padding: 0px 10px;
  margin: 0px 5px;
}

.sitebutton{
  font-family: 'Noto Sans JP', sans-serif;
  border: none;
  border-radius: 20px;
  background-color: #aac;
}

.add-sitebutton{
  font-family: 'Noto Sans JP', sans-serif;
  font-size: 1.1em;
  width: 30px;
  border: 1px solid #336;
  border-radius: 50%;
  background-color: var(--btn_color);
  color: #fff;
  margin: 0px 10px 0px 5px;
}

.toggle-button{
  font-size: 0.9em;
  width:150px;
  height:25px;
  margin-left:5px;
  background-color: #669;
  color:#fff;
  font-family: 'Noto Sans JP', sans-serif;
  border: none;
  border-radius: 20px;
  font-weight: bold;
  text-align: center;
}

.error{
  font-size: 1.0em;
  font-weight: bold;
  color:#f00;
  font-family: 'Noto Sans JP', sans-serif;
}

.main {
    width: 60%;
    min-width: 900px;
    height:100%;
    margin: 5px auto;
    display: flex;
    flex-direction: column;
}

.chatfield{
    width: 100%;
    margin: 50px auto;
    height: 100%;
    border: 1px solid #f0f0f0;
}

.chat_user{
    width:80%;
    border: 1px solid #ccc;
    color: #fff;
    background-color: var(--chat_color);
    padding: 5px 5px 5px 10px;
    margin: 10px auto 20px 30px;
    border-radius: 10px 10px 10px 0;
    box-shadow: 1px 2px 2px 0px #ccc;
}

.bing_query{
    font-size: 0.8em;
    width:100%;
    margin-left: auto;
    font-weight: bold;
    margin-bottom: 20px;
}

.bing_link{
  font-size:0.9em;
  margin-left: 20px;
}

.chat_assistant{
    width:80%;
    border: 1px solid #ccc;
    background-color: #fff;
    margin-left: auto;
    padding: 5px 5px 5px 10px;
    margin: 10px 30px 20px auto;
    border-radius: 10px 10px 0 10px;
    box-shadow: 1px 2px 2px 0px #ccc;
}

.chat_message{
    white-space: pre-wrap;
    font-size: 1.0em;
    font-family: 'Noto Sans JP', sans-serif;
}

.messagebox {
    width: 90%;
    height: 70px;
    resize: none;
    outline: none;
    background-color: #ffffff;
    margin:10px auto 0px auto;
    font-size: 1.0em;
    border: 3px solid #666;
    border-radius: 10px;
    font-family: 'Noto Sans JP', sans-serif;
}

.messagebox_bottom {
    width: 95%;
    height: 30px;
    text-align: right;
}

.button_send {
    font-size: 1.1em;
    padding: 10 20px;
    margin: 10px 0 0 10px;
    width:100px;
    background-color: var(--btn_color);
    color:#fff;
    font-family: 'Noto Sans JP', sans-serif;
    border: none;
    border-radius: 20px;
    font-weight: bold;
}

.button_send:active{
  transform: scale(1.2);
}

.button_clear {
    font-size: 1.1em;
    padding: 10 20px;
    margin: 10px 0 0 10px;
    width:100px;
    background-color: #999999;
    color:#fff;
    font-family: 'Noto Sans JP', sans-serif;
    border: none;
    border-radius: 20px;
    font-weight: bold;
}

.error{
    color: red;
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

@keyframes spin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}


</style>
