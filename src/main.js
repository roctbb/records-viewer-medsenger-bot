import Vue from 'vue'
import App from './App.vue'
import axios from "axios";
import vmodal from 'vue-js-modal'
import VueSimpleAlert from "vue-simple-alert";
import VueConfirmDialog from 'vue-confirm-dialog'

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
        group_by: function (data, field) {
            if (!data)
                return []

            return data.reduce((groups, item) => {
                const group = (groups[item[field] ? item[field] : 'Общее'] || []);
                group.push(item);
                groups[item[field] ? item[field] : 'Общее'] = group;
                return groups;
            }, {});
        }
    },
    computed: {
        mobile() {
            return window.innerWidth < window.innerHeight
        }
    },
    data() {
        return {
            images: {
                logo: 'https://common.medsenger.ru/images/logo.png',
                ok: 'https://common.medsenger.ru/images/icons8-ok-128.png',
                error: 'https://common.medsenger.ru/images/icons8-delete-128.png',
                nothing_found: 'https://common.medsenger.ru/images/icons8-nothing-found-100.png',
                warning: 'https://common.medsenger.ru/images/icons8-error-18.png',
                report: 'https://common.medsenger.ru/images/icons8-search-property-96.png',
                graph: 'https://common.medsenger.ru/images/icons8-graph-96.png',
                heatmap: 'https://common.medsenger.ru/images/icons8-heat-map-96.png',
                file: 'https://common.medsenger.ru/images/icons8-open-document-48.png'
            },
            axios: require('axios'),
            category_list: undefined,
            window_mode: window.MODE,
            object_id: window.OBJECT_ID,
            source: window.SOURCE
        }
    }
})

window.onresize = function () {
    Event.fire('window-resized')
}

Vue.use(vmodal, {componentName: 'Modal'})
Vue.use(VueConfirmDialog)
Vue.component('vue-confirm-dialog', VueConfirmDialog.default)
Vue.use(VueSimpleAlert);

new Vue({
    render: h => h(App),
}).$mount('#app')
