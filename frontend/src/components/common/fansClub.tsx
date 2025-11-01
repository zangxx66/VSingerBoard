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
        const memberImg = `${window.location.origin}/assets/images/subscribe_new_v3.png`

        return () => (
            <div class="fans-club-container">
                <img src={clubImg} alt="fansclub" class="fans-club-img" width="24" />
                {props.guard_level == 2 && (
                    <img src={memberImg} alt="member" class="fans-club-member-img" width="24" />
                )}
            </div>
        )
    }
})