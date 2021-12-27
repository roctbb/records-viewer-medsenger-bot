<template>
  <div>
    <input class="btn btn-link btn-sm text-muted" type="button" data-toggle="collapse" aria-expanded="false"
           :value="`+ ${title}:`" :data-target="'#collapse' + id" :aria-controls="'collapse' + id">
    <div class="collapse" :id="'collapse' + id">
      <div class="card card-body" style="padding: -20px">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "MoreInfoBlock",
  props: ['title', 'id']
}
</script>

<style scoped>
.card-body {
  background-color: transparent;
  border-color: transparent;
  padding: 0px;
}
</style>