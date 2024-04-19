<template>
  <div class="interactive-map" v-if="map">
    <human-map v-if="map == 'human'" :parts="parts" :id="id" :in_table="in_table"/>
    <child-map v-if="map == 'child'" :parts="parts" :id="id" :in_table="in_table"/>
  </div>
</template>

<script>

import HumanMap from "../../../maps/HumanMap.vue";
import ChildMap from "../../../maps/ChildMap.vue";

export default {
  name: "InteractiveMap",
  components: {HumanMap, ChildMap},
  props: ['map', 'parts', 'id', 'in_table']
}
</script>

<style scoped>
svg {
    background-color: #fcfcfc80;
}
</style>

