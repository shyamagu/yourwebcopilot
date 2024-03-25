import adapter from '@sveltejs/adapter-static';

export default {
    kit: {
        adapter: adapter({
            // default options are shown. On some platforms
            // these options are set automatically — see below
            pages: '../backend/static',
            assets: '../backend/static',
            fallback: null,
            precompress: false,
            strict: true
        })
    }
};