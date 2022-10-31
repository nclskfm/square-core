<!-- The Home Page. Questions are asked and the results are displayed here. -->
<template>
  <div>
    <form v-on:submit.prevent="askQuestion">
      <div id="carouselExampleControls" class="carousel carousel-dark slide" data-bs-ride="carousel">
        <div class="carousel-inner">
          <div class="carousel-item active">
            <div class="container d-block w-75">
              <SkillSelection v-on:input="changeSelectedSkills"/>
            </div>
          </div>
          <div class="carousel-item">
            <div class="container d-block w-75">
              <div class="row gy-5">

                <div class="col-4">
                  <div class="bg-light border border-success rounded shadow h-100 p-3">
                    <label for="question" class="form-label">2. Enter you question</label>
                    <textarea
                        v-model="currentQuestion"
                        @keydown.enter.exact.prevent
                        class="form-control form-control-lg mb-2"
                        id="question"
                        placeholder="Question"
                        required
                        style="resize: none; height: calc(48px * 2.25);"
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


                <div class="col-8" v-if="skillSettings.requiresContext && skillSettings.skillType != 'multiple-choice'">
                  <div class="bg-light border border-warning rounded shadow h-100 p-3">
                    <label for="context" class="form-label">3. Provide context</label>
                  <textarea 
                      v-if="skillSettings.skillType != 'multiple-choice'"
                      v-model="inputContext"
                      class="form-control form-control-lg mb-2"
                      id="context"
                      :placeholder="contextPlaceholder"
                      style="resize: none; height: calc(38px * 6);"
                      required />
                      </div>
                </div>

                <div class="col-8" v-if="!skillSettings.requiresContext && skillSettings.skillType == 'multiple-choice'">
                  <div class="bg-light border border-info rounded shadow h-100 p-3">
                    <label for="choices_loop" class="form-label">{{instructionChoices}}</label>
                    <div class="row g-0" v-for="(choice, index) in list_choices" :key="index" id="choices_loop">
                      <div class="col-sm">
                        <div class="input-group input-group-sm mb-3">
                          <span class="input-group-text" id="basic-addon1">{{index+1}}</span>
                          <input v-model="list_choices[index]" type="text" class="form-control form-control-sm">
                        </div>
                      </div>
                    </div>
                    <!-- button to add one more element to list_choices -->
                    <div class="form-inline">
                      <button type="button" class="btn btn-sm btn-outline-success" v-on:click="addChoice">Add Choice</button>
                      <!-- button to remove one element of list_choices -->
                      <button type="button" class="btn btn-sm btn-outline-danger" v-on:click="removeChoice">Remove Choice</button>
                    </div>

                  </div>
                </div>

                <div class="col-4" v-if="skillSettings.requiresContext && skillSettings.skillType == 'multiple-choice'">
                  <div class="bg-light border border-warning rounded shadow h-100 p-3">
                    <label for="context" class="form-label">3. Provide context</label>
                  <textarea 
                      v-model="inputContext"
                      class="form-control form-control-lg mb-2"
                      id="context"
                      :placeholder="contextPlaceholder"
                      style="resize: none; height: calc(38px * 6);"
                      required />
                      </div>
                </div>

                <div class="col-4" v-if="skillSettings.requiresContext && skillSettings.skillType == 'multiple-choice'">
                  <div class="bg-light border border-info rounded shadow h-100 p-3">
                    <label for="choices_loop" class="form-label">{{instructionChoices}}</label>
                    <div class="row g-0" v-for="(choice, index) in list_choices" :key="index" id="choices_loop">
                      <div class="col-sm">
                        <div class="input-group input-group-sm mb-3">
                          <span class="input-group-text" id="basic-addon1">{{index+1}}</span>
                          <input v-model="list_choices[index]" type="text" class="form-control form-control-sm">
                        </div>
                      </div>
                    </div>
                    <!-- button to add one more element to list_choices -->
                    <div class="form-inline">
                      <button type="button" class="btn btn-sm btn-outline-success" v-on:click="addChoice">Add Choice</button>
                      <!-- button to remove one element of list_choices -->
                      <button type="button" class="btn btn-sm btn-outline-danger" v-on:click="removeChoice">Remove Choice</button>
                    </div>

                  </div>
                </div>

              </div> <!-- row -->

              <div class="row gy-5" v-if="failure">
                <div class="col-auto">
                  <Alert class="bg-warning" :dismissible="true">An error occurred</Alert>
                </div>
              </div>


              <div class="row gy-5" v-if="minSkillsSelected(1)">
                <div class="col-4"></div>
                
                <div class="col-4">
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
                <div class="col-4"></div>
              </div>

              <div v-if="this.feedback" class="row mt-4">
                <div class="d-grid gap-1 d-md-flex justify-content-md-center">
                  <a v-on:click="askQuestionWithFeedback()" role="button" class="btn btn-warning shadow">
                    Re-ask with feedback
                  </a>
                </div>
              </div>


            </div>
          </div>
          <div class="carousel-item">
            <div class="container d-block w-75">
              <Results v-if="isShowingResults" />
            </div>
          </div>
        </div>
        <button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleControls" data-bs-slide="prev">
          <span class="carousel-control-prev-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Previous</span>
        </button>
        <button class="carousel-control-next" type="button" data-bs-target="#carouselExampleControls" data-bs-slide="next">
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
/* eslint-disable */
import Alert from '../components/Alert'

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
      inputChoices: '',
      list_choices: ["", "", ""],
      failure: false,
      skillSettings: {
        skillType: null,
        requiresContext: false,
        requiresMultipleChoices: 0
      },
      feedbackDocuments: [],
      feedback: false,
    }
  },
  components: {
    SkillSelection,
    Results,
    Alert
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
    instructionChoices(){
      if (!this.skillSettings.requiresContext) {
        return "3. Provide a list of answer choices"
      } else {
        return "4. Provide a list of answer choices"
      }
    },
  },
  mounted() {
    this.$root.$on("addFeedbackDocument", (feedbackDoc) => {
      this.feedbackDocuments.push(feedbackDoc)
      this.feedback = true
    })
  },
  methods: {
    changeSelectedSkills(options, skillSettings) {
      this.options = options
      this.skillSettings = skillSettings
    },
    minSkillsSelected(num) {
      return this.selectedSkills.length >= num
    },
    addChoice() {
      this.list_choices.push("")
    },
    removeChoice() {
      // we always need at least 2 choices
      if (this.list_choices.length > 2) {
        this.list_choices.pop()
      } else {
        alert("You need at least 2 choices")
      }
      
    },
    askQuestion() {
      // if skill does not require context, set context to null
      if (!this.skillSettings.requiresContext) {
        this.inputContext = ""
      }
      this.waiting = true
      this.$store.dispatch('query', {
        question: this.inputQuestion,
        inputContext: this.inputContext,
        choices: this.list_choices,
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
      this.list_choices = ["", "", ""]
      this.inputQuestion = example.query
      if (this.skillSettings.requiresContext) {
        this.inputContext = example.context
      }
      if (example.choices) {
        this.list_choices = example.choices.map((x) => x);
      }
      this.askQuestion()
    },
    askQuestionWithFeedback() {
      this.waiting = true
      this.$store.dispatch('query', {
        question: this.inputQuestion,
        inputContext: this.inputContext,
        options: {
          selectedSkills: this.selectedSkills,
          maxResultsPerSkill: this.options.maxResultsPerSkill,
          feedback_documents: this.feedbackDocuments
        }
      }).then(() => {
        this.failure = false
      }).catch(() => {
        this.failure = true
      }).finally(() => {
        this.waiting = false
      })
      this.$root.$emit('clearUpvotes');
      this.feedbackDocuments = []
    }
  }
})
</script>