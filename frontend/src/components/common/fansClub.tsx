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
        const medalNameBg = `${window.location.origin}/assets/images/star_guard_advanced_badge_${props.medal_level}_xmp.png`
        const bgColor = props.medal_level && props.medal_level <= 10 ? "#fab80c" : "#ff6c19"

        return () => (
            <div class="fans-club-container">
                <img src={clubImg} alt="fansclub" class="fans-club-img" width="24" />
                {props.medal_name && (
                    <div class="fans-club-name-container" style={{ backgroundColor: bgColor }}>
                        <img src={medalNameBg} alt="medalNameBg" class="fans-club-name-bg" />
                        <span class="fans-club-name">{props.medal_name}</span>
                    </div>
                )}
                {props.guard_level == 2 && (
                    <img src={memberImg} alt="member" class="fans-club-member-img" width="24" />
                )}
            </div>
        )
    }
})