import {Link} from 'react-router-dom';
import styles from './styles/Landing.module.css';
import shadow from '../components/shadow.png';
import noShadow from '../components/no shadow.png';

function Landing() {
    return(
    <>
        <br/><br/><br/>

        <div className={styles.title}>
            <span className={styles.bigFont}>AR</span>
            <span style={{fontSize: '30px'}}>ithmetic</span>
            <Link to ="/other" className={styles.imageHover}>
                <img src={shadow} alt = 'shadow' className = {styles.normal} />
                <img src={noShadow} alt = 'no shadow' className = {styles.hover} />
            </Link>
        </div>

        <div>
            <p>
                So we made an app that's basically photomath but marginally better.
            </p>
        </div>
    </>
    )    
}

export default Landing;