export default defineComponent({
    name: "FansClub",
    props: {
        medalName: {
            type: String,
            default: ""
        },
        medalLevel: {
            type: Number,
            default: 0
        },
        guardLevel: {
            type: Number,
            default: 0
        }
    },
    setup(props) {
        const clubImg = `${window.location.origin}/images/fansclub_new_advanced_badge_${props.medalLevel}_xmp.png`
        const memberImg = `${window.location.origin}/images/subscribe_new_v3.png`
        const medalNameBg = `${window.location.origin}/images/star_guard_advanced_badge_${props.medalLevel}_xmp.png`
        const bgColor = props.medalLevel && props.medalLevel <= 10 ? "#fab80c" : "#ff6c19"

        return () => (
            <div class="fans-club-container">
                <img src={clubImg} alt="fansclub" class="fans-club-img" width="24" />
                {props.medalName && (
                    <div class="fans-club-name-container" style={{ backgroundColor: bgColor }}>
                        <img src={medalNameBg} alt="medalNameBg" class="fans-club-name-bg" />
                        <span class="fans-club-name">{props.medalName}</span>
                    </div>
                )}
                {props.guardLevel == 2 && (
                    <img src={memberImg} alt="member" class="fans-club-member-img" width="24" />
                )}
            </div>
        )
    }
})