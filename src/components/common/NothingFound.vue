<template>
    <div style="margin-top: 50px">
        <p style="text-align: center"><img :src="images.nothing_found"/></p>

        <p style="text-align: center">
            <small v-if="message">{{message}}</small>
            <small v-else>Нет данных за выбранный период.</small>
        </p>
    </div>
</template>

<script>
export default {
    name: "NothingFound",
    props: ['message']
}
</script>

<style scoped>

</style>