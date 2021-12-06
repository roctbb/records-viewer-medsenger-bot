import Vue from 'vue'
import App from './App.vue'
import axios from "axios";
import vmodal from 'vue-js-modal'
import VueSimpleAlert from "vue-simple-alert";

window.Event = new class {
    constructor() {
        this.vue = new Vue();
    }

    fire(event, data = null) {
        if (!data) {
            console.log('sending event', event);
        } else {
            console.log('sending event', event, 'with data', data);
        }

        this.vue.$emit(event, data);
    }

    listen(event, callback) {
        this.vue.$on(event, callback);
    }
};

Vue.mixin({
    methods: {
        url: function (action) {
            let api_host = window.API_HOST;
            let agent_token = window.AGENT_TOKEN;
            let contract_id = window.CONTRACT_ID;
            let agent_id = window.AGENT_ID;

            return api_host + '/api/client/agents/' + agent_id + '/?action=' + action + '&contract_id=' + contract_id + '&agent_token=' + agent_token
        },
    },
    computed: {
        mobile() {
            return window.innerWidth < window.innerHeight
        }
    },
    data() {
        return {
            images: {
                logo: window.LOCAL_HOST + '/static/logo.png',
                ok: window.LOCAL_HOST + '/static/icons/icons8-ok-128.png',
                error: window.LOCAL_HOST + '/static/icons/icons8-delete-128.png',
                nothing_found: window.LOCAL_HOST + '/static/icons/icons8-nothing-found-100.png',
            },
            axios: require('axios'),
            category_list: window.CATEGORY_LIST
        }
    }
})

Vue.use(vmodal, {componentName: 'Modal'})
Vue.use(VueSimpleAlert);

new Vue({
    render: h => h(App),
}).$mount('#app')
