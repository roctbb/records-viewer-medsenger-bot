<template>
    <div class="card" :style="bg">
        <div class="card-body" :style="additional_style ? additional_style : ''">
            <h6 class="card-title" v-if="title && !big">{{ title }}</h6>
            <h5 class="card-title" v-if="title && big">{{ title }}</h5>
            <slot></slot>
        </div>
    </div>
</template>

<script>
export default {
    name: "Card",
    props: ['title', 'image', 'additional_style', 'big'],
    computed: {
        bg: function () {
            let size = `background-size: ${this.big ? 40 : 55}px;`
            if (this.image) {
                return "background-image: url('" + this.image + "'); " + size
            } else {
                return "background-image: none;" + size
            }
        }
    }
}
</script>

<style scoped>
.card {
    margin-bottom: 15px;
    background-repeat: no-repeat;
    background-position: right 5px bottom 5px;
    height: 90%;
}

.card a {
    font-size: 0.75rem;
}

.card-body {
    display: flex;
    flex-flow: column;
    justify-content: space-between;
    align-items: start;
}
</style>
