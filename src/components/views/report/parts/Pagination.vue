<template>
    <div>
        <ul class="pagination pagination-sm justify-content-center">
            <li class="page-item">
                <button class="page-link" aria-label="First"
                        @click="change_page(1)"
                        :disabled="selected_page == 1">
                    <span aria-hidden="true">&#8676;</span>
                </button>
            </li>
            <li class="page-item">
                <button class="page-link" aria-label="Previous"
                        @click="change_page(selected_page - 1)"
                        :disabled="selected_page == 1">
                    <span aria-hidden="true">&#8592;</span>
                </button>
            </li>

            <li class="page-item" v-for="i in pages">
                <button :class="`page-link ${i == selected_page ? 'active' : ''}`" @click="change_page(i)">{{ i }}</button>
            </li>

            <li class="page-item">
                <button class="page-link" aria-label="Next"
                        @click="change_page(selected_page + 1)"
                        :disabled="selected_page == page_cnt">
                    <span aria-hidden="true">&#8594;</span>
                </button>
            </li>
            <li class="page-item">
                <button class="page-link" aria-label="last"
                        @click="change_page(page_cnt)"
                        :disabled="selected_page == page_cnt">
                    <span aria-hidden="true">&#8677;</span>
                </button>
            </li>
        </ul>
    </div>
</template>

<script>
export default {
    name: "Pagination",
    props: ['selected_page', 'page_cnt'],
    computed: {
        pages() {
            let pages = this.range_arr(this.page_cnt, 1)
            let pages_to_show = []
            let max = this.mobile ? 5 : 21
            let offset = Math.ceil(max / 2)

            if (this.page_cnt > max) {
                if (this.selected_page <= offset)
                    pages_to_show = pages.slice(0, max)
                else if (this.page_cnt - this.selected_page <= offset)
                    pages_to_show = pages.slice(this.page_cnt - max, this.page_cnt)
                else
                    pages_to_show = pages.slice(this.selected_page - offset, this.selected_page + offset)
                return pages_to_show
            }

            return pages
        }
    },
    methods: {
        change_page: function (page) {
            Event.fire('select-page', page)
        },
    },
    mounted() {
    }
}
</script>

<style scoped>
.pagination {
    margin: 5px;
}

.page-link {
    color: #006c88;
}

.active {
    color: #fcfcfc;
    background-color: #24a8b4;
}
</style>