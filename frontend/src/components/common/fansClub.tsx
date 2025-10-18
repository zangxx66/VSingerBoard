import { defineComponent } from "vue"

export default defineComponent({
    name: "fansClub",
    props: {
        medal_name: {
            type: String
        },
        medal_level: {
            type: Number
        },
        guard_level: {
            type: Number
        }
    },
    setup(props) {
        const clubImg = `${window.location.origin}/assets/images/fansclub_new_advanced_badge_${props.medal_level}_xmp.png`

        return () => (
            <div class="fans-club-container" style="padding-right: 5px;">
                <img src={clubImg} alt="fansclub" class="fans-club-img" width="24" />
            </div>
        )
    }
})