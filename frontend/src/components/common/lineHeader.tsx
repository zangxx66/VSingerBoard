import { defineComponent } from "vue"

export default defineComponent({
    name: "lineHeader",
    props: {
        title: {
            type: String,
            required: true
        }
    },
    setup(props) {
        return () => (
            <div class="line-header">
                <div class="line-header-title">{props.title}</div>
            </div>
        )
    }
})