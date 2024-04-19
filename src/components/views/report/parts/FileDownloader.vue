<template>
    <div>
        <span class="text-muted" v-if="!file_description || file == 'not-found'">Файл не найден...</span>
        <div class="row" v-else>
            <img :src="images.file" height="20" style="margin-right: 5px"/>
            <a href="#" @click="get_file('download')">{{ file_description.name }} (скачать)</a>
        </div>

        <div v-if="file != 'not-found' && file_description.type.includes('image')">
            <div v-if="show_img && file">
                <img :src="`data:${file_description.type};base64,${file.base64}`"
                     :style="`max-width: ${img_width}; max-height: ${img_height};`"/>
            </div>

            <more-info-block title="Показать изображение" :id="`file_${file_description.id}`" v-if="!show_img">
                <loading v-if="!file"/>
                <img :src="`data:${file_description.type};base64,${file.base64}`"
                     :style="`max-width: ${img_width}px; max-height: ${img_height}px;`" v-else/>
            </more-info-block>
        </div>
    </div>
</template>

<script>
import MoreInfoBlock from "./MoreInfoBlock.vue";
import Loading from "../../../common/Loading.vue";
import downloadjs from "downloadjs";

export default {
    name: "FileDownloader",
    components: {Loading, MoreInfoBlock},
    props: {
        file_description: {required: true},
        show_img: {required: true},
        in_table: {required: false}
    },
    data() {
        return {
            file: undefined
        }
    },
    created() {
        if (!this.file_description) this.file = 'not-found'
        if (this.show_img) this.get_file('show', false)

        Event.listen('open-more-info', (id) => {
            if (id.includes('file')) {
                let file_id = parseInt(id.replace('file_', '').split('_'))
                if (file_id != this.file_description.id) return

                if (!this.file) {
                    this.get_file('show')
                }
            }
        })

    },
    methods: {
        get_file: function (action, show_error = true) {
            if (this.file) {
                if (action == 'download' && this.file != 'not-found')
                    downloadjs(`data:${this.file_description.type};base64,${this.file.base64}`, this.file_description.name, this.file_description.type);
                return
            }

            this.axios
                .get(this.direct_url('/api/get_file/' + this.file_description.id))
                .then(response => {
                    this.file = response.data
                    if (action == 'download')
                        downloadjs(`data:${this.file_description.type};base64,${this.file.base64}`, this.file_description.name, this.file_description.type);
                    this.$forceUpdate()
                })
                .catch((e) => {
                    this.file = 'not-found'
                    this.$forceUpdate()
                    if (show_error) Event.fire('load-error')
                });
        }
    },
    computed: {
        img_width() {
            if (this.to_export) return '500px'
            return '90%'
        },
        img_height() {
            if (this.to_export) return '500px'
            return  '90%'
        }
    }
}
</script>

<style scoped>

</style>