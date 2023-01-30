<template>
  <div>
    <multiselect
      id="metric_evaluation"
      v-model="value"
      :options="metrics"
      placeholder="Select the name of metric"
      label="label"
      track-by="id"
      :custom-label="labelWithCity"
      :multiple="false"
      :clear-on-select="true"
      :close-on-select="true"
      :show-no-results="true"
      :hide-selected="false"
      :allow-empty="true"

    >

      <!-- affichage du multiselect plié -->
      <template slot="singleLabel" slot-scope="{ option }">
        <strong>{{ option }}</strong>
        <!-- <span style="color: red">&nbsp;{{ option}}</span> -->
      </template>
      <!-- affichage des options(multiselect déplié) -->
      <template slot="option" slot-scope="{ option }">
        <div class="option__desc">
          <span class="option__title" >
            <strong>{{ option }}&nbsp;</strong>
          </span>
          <!-- <span class="option__small" style="color: green">{{
            option
          }}</span> -->
        </div>
      </template>
    </multiselect>
  </div>
</template>
<script>
import Multiselect from "vue-multiselect";

export default {
  components: {
    Multiselect,
  },

  data() {
    return {
      value: null,
      metrics: ["squad", "squad_v2", "exact_match"],
    };
  },
  methods: {
    //l'affichage des options lorsqu'il n'y a pas de template avec slot=singleLabel ou slot=option
    labelWithCity({ label, city }) {
      return `${label} — [${city}]`;
    },
  },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
