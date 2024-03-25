<script>
    import { onMount } from 'svelte';

    let message = 'loading...';
    
    async function callApi() {
        const response = await fetch('/api');
        const data = await response.json();
        message = data.message;
    }

    onMount(() => {
        callApi();
    });
    
</script>

<h1>Hello</h1>
<p>{message}</p>
