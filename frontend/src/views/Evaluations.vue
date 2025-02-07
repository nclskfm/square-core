<!-- The Evaluations Overview Page. The user can see their own and all public evaluations here. They can delete and add new evaluations -->
<template>
  <Card title="Evaluations">
    <template #rightItem>
      <router-link to="new_evaluation" class="btn btn-outline-danger d-inline-flex align-items-center" role="button">
        <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-plus-square" viewBox="0 0 16 16">
          <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
          <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
        </svg>
        &nbsp;New
      </router-link>
    </template>
    <div class="list-group list-group-flush">
      <li
          v-for="evaluation in items"
          :key="evaluation.evaluation_id"
          class="list-group-item bg-transparent py-4">
        <div class="d-flex w-100 justify-content-between">
          <h5 class="mb-1">{{evaluation.skill_name}}</h5>
          <small>
            <ExpandButton v-if="evaluation.evaluation_status !== 'RUNNING'" :evaluation="evaluation"></ExpandButton>
          </small>
        </div>
        <div>
          <BIconBookmarks width="24" height="24"/>
          <span style="display:inline-block; width: 5px;"></span>
          <span style="font-size: 16px">{{evaluation.dataset}}</span>
          <span style="display:inline-block; width: 10px;"></span>
          <BIconBarChart width="24" height="24"/>
          <span style="display:inline-block; width: 6px;"></span>
          <span style="font-size: 16px">{{evaluation.metric_name}}</span>
        </div>
        <span style="display:block; height: 5px;"></span>
        <Status :url="evaluation.skill_url" /> 
        <span v-if=evaluation.public class="badge bg-info ms-1 p-2">Public</span>
        <span v-else class="badge bg-secondary ms-1 p-2">Private</span>
        <span v-if="evaluation.evaluation_status == 'FINISHED'" class="badge bg-success ms-1 p-2">{{ evaluation.evaluation_status }}</span>
        <span v-if="evaluation.evaluation_status == 'FAILED'" class="badge bg-danger ms-1 p-2">{{ evaluation.evaluation_status }}</span>
        <span v-if="evaluation.evaluation_status == 'RUNNING'" class="badge bg-warning ms-1 p-2">{{ evaluation.evaluation_status }}</span>
        
        <CardExpansion :evaluation="evaluation"></CardExpansion>
      </li>
    </div>
    <div v-if="!items.length" class="p-5 text-center">
      <div class="feature-icon bg-danger bg-gradient">
        <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-question-lg" viewBox="0 0 16 16">
          <path fill-rule="evenodd" d="M4.475 5.458c-.284 0-.514-.237-.47-.517C4.28 3.24 5.576 2 7.825 2c2.25 0 3.767 1.36 3.767 3.215 0 1.344-.665 2.288-1.79 2.973-1.1.659-1.414 1.118-1.414 2.01v.03a.5.5 0 0 1-.5.5h-.77a.5.5 0 0 1-.5-.495l-.003-.2c-.043-1.221.477-2.001 1.645-2.712 1.03-.632 1.397-1.135 1.397-2.028 0-.979-.758-1.698-1.926-1.698-1.009 0-1.71.529-1.938 1.402-.066.254-.278.461-.54.461h-.777ZM7.496 14c.622 0 1.095-.474 1.095-1.09 0-.618-.473-1.092-1.095-1.092-.606 0-1.087.474-1.087 1.091S6.89 14 7.496 14Z"/>
        </svg>
      </div>
      <h2 class="display-5">New Evaluations</h2>
      <p class="lead fs-2">Add new evaluations to the <span class="text-danger">UKP-SQuARE</span> platform.</p>
      <p class="lead fs-2">Evaluations can be <span class="text-danger">publicly</span> available or set to <span class="text-danger">private</span>.</p>
      <p class="lead fs-2"><span class="text-danger">Get started</span> by creating a new evaluation.</p>
      <div class="d-grid gap-2 d-flex justify-content-center">
        <router-link to="/new_evaluation" class="btn btn-outline-danger btn-lg px-4 d-inline-flex align-items-center">
          Add a new evaluation
        </router-link>
      </div>
    </div>
  </Card>
</template>


<script>
import Vue from 'vue'
import Card from '@/components/Card.vue'
import ExpandButton from '@/components/ExpandButton.vue'
import CardExpansion from '@/components/CardExpansion.vue'
import Status from '@/components/Status.vue'
import { getEvaluations } from '@/api'
import { BIconBarChart, BIconBookmarks} from 'bootstrap-vue'


export default Vue.component('list-evaluations', {
  components: {
    Card,
    CardExpansion,
    ExpandButton,
    Status,
    BIconBookmarks,
    BIconBarChart
  },
  methods: {
    evaluations() {
      setTimeout(function() {
        getEvaluations(this.$store.getters.authenticationHeader())
          .then((response) => {
            this.items = response.data
          })
      }.bind(this), 50)
    }
  },
  data() {
    return {
      items: []
    }
  },
  beforeMount() {
    this.evaluations()
  }
})
</script>
