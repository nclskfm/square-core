<!-- The Home Page. Questions are asked and the results are displayed here. -->
<template>
  <div>
    <form v-on:submit.prevent="askQuestion">
    <div id="carouselExampleIndicators" class="carousel carousel-dark" data-bs-interval="false">
      <div class="carousel-indicators">
        <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="0" class="active" aria-current="true" aria-label="Slide 1"></button>
        <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="1" aria-label="Slide 2"></button>
        <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="2" aria-label="Slide 3"></button>
      </div>
      <div class="carousel-inner" >
        <div class="carousel-item active" data-bs-interval="false" >
          <div class="d-flex justify-content-center w-100 h-100">
            <SkillSelection v-on:input="changeSelectedSkills"/>
          </div>
        </div>


        <div class="carousel-item" data-bs-interval="false"  >
          <div class="d-flex justify-content-center">
            <div class="container text-center">
              <div class="row">
                <div class="col">
                  <div class="bg-light border border-success rounded shadow p-3">
                    <label for="question" class="form-label">2. Enter you question</label>
                    <textarea
                        v-model="currentQuestion"
                        @keydown.enter.exact.prevent
                        class="form-control form-control-lg mb-2"
                        id="question"
                        placeholder="Question"
                        required
                        :disabled="!minSkillsSelected(1)" />
                    <p v-if="currentExamples.length > 0" class="form-label">Or try one of these examples</p>
                    <div class="row" v-for="(example, index) in currentExamples" :key="index">
                      <div class="col-auto">
                        <span
                            role="button"
                            v-on:click="selectExample(example)"
                            class="badge bg-success text-wrap lh-base w-100">{{ example.query }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col">
                  <div v-if="skillSettings.requiresContext" class="col-auto">
                  <div class="bg-light border border-warning rounded shadow p-3">
                      <label for="context" class="form-label">3. Provide context</label>
                      <textarea
                          v-model="inputContext"
                          class="form-control mb-2"
                          id="context"
                          style="resize: none; height: calc(38px * 7);"
                          :placeholder="contextPlaceholder"
                          required />
                      <small class="text-muted">{{ contextHelp }}</small>
                  </div>
                </div>

                </div>
                <div class="col">
                  Column
                </div>
              </div>

              <div class="row">
                <div class="col">
                  <div v-if="failure" class="row">
                <div class="col-md-4 mx-auto mt-4">
                  <Alert class="bg-warning" :dismissible="true">An error occurred</Alert>
                </div>
              </div>
              <div v-if="minSkillsSelected(1)" class="row">
                <div class="col auto">
                  <div class="d-grid gap-2 d-md-flex justify-content-md-center">
                    <button
                        type="submit"
                        class="btn btn-danger btn-lg shadow text-white"
                        :disabled="waiting"
                        data-bs-target="#carouselExampleIndicators" data-bs-slide-to="2" aria-label="Slide 3">
                      <span v-show="waiting" class="spinner-border spinner-border-sm" role="status" />
                      &nbsp;Ask your question</button>
                  </div>
                </div>
              </div>
                </div>
                
              </div>
            </div>


            
          </div>
        </div>
        <div class="carousel-item" data-bs-interval="false">
          <div class="d-flex justify-content-center">
            <!-- <Results  /> -->
            <div class="container text-center">
              <div class="row">
                <div class="col">
                  <h1>{{inputQuestion}}</h1>
                </div>
            </div>
            <div class="row">
              <div class="col">
                <Results  />
              </div>
            </div>
            </div>
            
          </div>
        </div>

      </div>
      <button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="prev">
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Previous</span>
      </button>
      <button class="carousel-control-next" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="next">
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Next</span>
      </button>
    </div>
    
    </form>
  </div>
</template>

<script>
import Vue from 'vue'
import SkillSelection from '@/components/SkillSelection.vue'

import Results from '@/components/Results.vue'

export default Vue.component('square-home', {
  data() {
    return {
      waiting: false,
      options: {
        selectedSkills: []
      },
      inputQuestion: '',
      inputContext: '',
      failure: false,
      skillSettings: {
        skillType: null,
        requiresContext: false,
        requiresMultipleChoices: 0
      }
    }
  },
  components: {
    SkillSelection,
    Results
  },
  computed: {
    isShowingResults() {
      return this.$store.state.currentResults.length > 0
    },
    selectedSkills() {
      return this.options.selectedSkills.filter(skill => skill !== 'None')
    },
    currentQuestion: {
      get: function () {
        return this.inputQuestion
      },
      set: function (newValue) {
        let tmp = newValue.trimEnd().split('\n')
        this.inputQuestion = tmp.splice(0, 1)[0]
        if (tmp.length > 0) {
          this.inputContext = tmp.join('\n')
        }
      }
    },
    currentExamples() {
      // Pseudo random return 3 examples from currently selected skills
      return this.$store.state.availableSkills
          .filter(skill => skill.skill_input_examples !== null
              && skill.skill_input_examples.length > 0
              && this.selectedSkills.includes(skill.id))
          .flatMap(skill => skill.skill_input_examples)
          .sort(() => 0.5 - Math.random())
          .slice(0, 3)
    },
    contextPlaceholder() {
      if (this.skillSettings.requiresMultipleChoices) {
        let choices = this.skillSettings.requiresMultipleChoices
        return `Provide ${choices > 1 ? choices + ' lines' : 'one line'} of context`
      } else {
        return 'No context required'
      }
    },
    contextHelp() {
      let help = 'no'
      if (this.skillSettings.requiresMultipleChoices) {
        let choices = this.skillSettings.requiresMultipleChoices
        help = `${choices > 1 ? choices + ' lines' : 'one line'} of`
      }
      return `Your selected skills require ${help} context.`
    }
  },
  methods: {
    changeSelectedSkills(options, skillSettings) {
      this.options = options
      this.skillSettings = skillSettings
    },
    minSkillsSelected(num) {
      return this.selectedSkills.length >= num
    },
    askQuestion() {
      this.waiting = true
      this.$store.dispatch('query', {
        question: this.inputQuestion,
        inputContext: this.inputContext,
        options: {
          selectedSkills: this.selectedSkills,
          maxResultsPerSkill: this.options.maxResultsPerSkill
        }
      }).then(() => {
        this.failure = false
      }).catch(() => {
        this.failure = true
      }).finally(() => {
        this.waiting = false
      })
    },
    selectExample(example) {
      this.inputQuestion = example.query
      if (this.skillSettings.requiresContext) {
        this.inputContext = example.context
      }
      this.askQuestion()
    }
  }
})
</script>