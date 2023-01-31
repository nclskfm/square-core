<template>
  <div>
    <multiselect
      id="skill_evaluation"
      v-model="value"
      :options="options"
      placeholder="Select the name of Skill"
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
import { getSkills } from '@/api'
export default {
  components: {
    Multiselect,
  },
  data() {
    return {
      list_skills: [],
      value: null,
      options: [],
    };
  },
  beforeMount() {
  getSkills(this.$store.getters.authenticationHeader())
      .then((response) => {
        // iterate over the skills and add the name to the list
        for (let i = 0; i < response.data.length; i++) {
          this.options.push(response.data[i].name)
        }
        return this.options;
      })
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
